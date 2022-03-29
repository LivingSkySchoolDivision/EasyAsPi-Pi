import logging
import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium
from os import path, system, getcwd
import requests
from time import sleep

API_HEARTBEAT_URI = "https://envirosaurus.lskysd.ca/Heartbeat"


# #########################################################
# Function definitions and initialization stuff
# #########################################################

logging.basicConfig(filename = "/var/log/EasyAsPi.log",level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:on line %(lineno)d:%(message)s")

def log_this(text):
    print(text)
    logging.info(text)

def serialize(things):
    string = "{"
    is_first = True
    for key in things:
        if  not is_first:
            string += ","
        else:
            is_first = False
        string += '"'
        string += key
        string += '"'
        string += ":"
        string += '"'
        string += things[key]
        string += '"'
    string += "}"
    return string

def get_serial():
    with open("/proc/cpuinfo","r") as cpuinfo_file:
        for line in cpuinfo_file:
            if line[0:6]=="Serial":
                return line[10:-1]

def get_model():
    with open("/proc/cpuinfo","r") as cpuinfo_file:
        for line in cpuinfo_file:
            if line[0:5]=="Model":
                return line[9:-1]

# Initialize the display
onboardScreen = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
onboardScreen.begin()

def display_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Black")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="Gray")
    onboardScreen.display(newImage)

def display_special_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Blue")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="white")
    onboardScreen.display(newImage)

def display_error_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Red")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="white")
    onboardScreen.display(newImage)

display_text_on_screen("Initializing...", 20)

# Initialize a reboot flag that we'll use later
reboot = False

# #########################################################
# Check for important files that might need to be created
# #########################################################
current_directory= f"{path.dirname(__file__)}/"
if not path.exists(current_directory +"version"):
    log_this("Creating empty version file")
    with open(current_directory +"version", "w") as version_file:
        version_file.write("DEFAULT")


# #########################################################
# Check to see if we need to change the hostname
# #########################################################

# Check hostname to make sure it's accurate
expected_hostname =f"EaP{get_serial()}"
display_text_on_screen("Checking hostname...", 20)

with open("/etc/hostname","r") as hostname_file:
    hostname = hostname_file.readline().strip()

if hostname != expected_hostname:
    log_this("changing hostname")
    sleep(5)
    with open("/etc/hostname","w") as hostname_file:
        hostname_file.write(expected_hostname)
    log_this("Rebooting to change hostname in 5 seconds...")
    display_text_on_screen("Rebooting for hostname...", 15)
    sleep(5)
    system("/sbin/reboot")
    quit()


# #########################################################
# Attempt to register with API
# #########################################################
api_success = False

# Build heartbeat payload
heartbeat_request_content = {"deviceSerialNumber":get_serial(),"deviceModel":get_model()}

# Wait a few seconds for WiFi to connect...
log_this("Waiting for WiFi...")
display_text_on_screen("Waiting for WiFi...", 20)
sleep(10)

for attempt_number in range(10):
    log_this(f"Making request to API {attempt_number}: " + API_HEARTBEAT_URI)
    display_text_on_screen(f"API {attempt_number+1}", 20)
    try:
        response =  requests.post(API_HEARTBEAT_URI,data=serialize(heartbeat_request_content),headers={"Content-Type":"application/json"})
        api_response = response.json()

        if response.ok:
            display_text_on_screen(f"API {attempt_number+1} OK", 20)
            log_this("Received response from API")
            api_success = True
            break
        else:
            display_error_text_on_screen(f"API {attempt_number+1} FAIL", 20)
            logging.error(f"Received error from API:{api_response}")
            print(api_response)
    except Exception as e:
        logging.error(e)
        display_error_text_on_screen(f"API {attempt_number+1} FAIL (E)", 20)
        log_this("ERROR RETRIEVING FROM API")
        sleep(2)
    if api_success:
        break
    display_error_text_on_screen("Retry in 10...", 20)
    sleep(10)

if not api_success:
    log_this("Could not get response from API. Quitting.")
    display_error_text_on_screen("COMMS FAIL".format(attempt_number), 20)
    quit()


# #########################################################
# Check the software version based on API response
# #########################################################

log_this("Checking version")
display_text_on_screen("Version check...", 20)

with open(current_directory +"version","r") as version_file:
    local_version = version_file.readline().strip()

log_this(f"Found local version: {local_version}")
log_this(f"Found remote version: {api_response['versionNumber']}")

if api_response["versionNumber"] != local_version:
    display_text_on_screen("Updating...", 20)
    log_this("Performing git pull")
    system("git pull --no-rebase")
    log_this("Updating version number")
    with open(current_directory +"version","w") as version_file:
        display_text_on_screen(api_response['versionNumber'], 20)
        version_file.write(api_response["versionNumber"])
    reboot = True
else:
    display_text_on_screen("Version OK", 20)
    log_this("Version OK")

# Check if we need to reboot from the reboot flag
if reboot:
    log_this("Rebooting due to flag being raised")
    display_special_text_on_screen("REBOOTING...", 20)
    system("/sbin/reboot")
    quit()


# #########################################################
# Display the assigned number on the onboard screen
# #########################################################

text_str = ""
if api_response["assignedNumber"]<100:
    text_str+="0"
    if api_response["assignedNumber"]<10:
        text_str+="0"

log_this("Displaying assigned number on screen: " + text_str)
text_str+=str(api_response["assignedNumber"])
display_text_on_screen(text_str, 94, -15)


# #########################################################
# Done!
# #########################################################

log_this("FIN")