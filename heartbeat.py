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

def get_version():
    with open(f"{path.dirname(__file__)}/version","r") as version_file:
        return version_file.readline().strip()

# Initialize the display
onboardScreen = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
onboardScreen.begin()

def display_assigned_number_on_screen(assigned_number, version_number):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Black")
    ImageDraw.Draw(newImage).text((0,-15),assigned_number, font=ImageFont.truetype(RobotoMedium, 85), fill=(0,100,0))
    ImageDraw.Draw(newImage).text((0,70),version_number, font=ImageFont.truetype(RobotoMedium, 10), fill=(64,64,64))
    onboardScreen.display(newImage)

def display_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Black")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="White")
    onboardScreen.display(newImage)

def display_special_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Green")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="Blue")
    onboardScreen.display(newImage)

def display_error_text_on_screen(text, size=40, yoffset=15):
    newImage = Image.new('RGB', (onboardScreen.width, onboardScreen.height), color="Red")
    ImageDraw.Draw(newImage).text((0,yoffset),text, font=ImageFont.truetype(RobotoMedium, size), fill="white")
    onboardScreen.display(newImage)

display_text_on_screen("Initializing...", 20)

# Initialize a reboot flag that we'll use later
reboot = False

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
local_version = get_version()
log_this(f"Found local version to be {local_version}")
heartbeat_request_content = {"deviceSerialNumber":get_serial(),"deviceModel":get_model(),"DeviceVersion":local_version}

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

log_this(f"Found local version: {local_version}")
log_this(f"Found remote version: {api_response['versionNumber']}")

if api_response["versionNumber"] != local_version:
    display_text_on_screen("Updating...", 20)
    log_this(f"Performing git pull in {path.dirname(__file__)}")
    system(f"cd {path.dirname(__file__)} && git fetch --all && git reset --hard origin/main")
    sleep(10)
    reboot = True
else:
    display_text_on_screen("Version OK", 20)
    sleep(1)
    log_this("Version OK")


# #########################################################
# Check if we need to reboot from the reboot flag
# #########################################################
if reboot:
    log_this("Rebooting due to flag being raised")
    display_special_text_on_screen("REBOOTING...", 20)
    system("/sbin/reboot")
    quit()


# #########################################################
# Display the assigned number on the onboard screen
# #########################################################

assigned_number_text = ""
if api_response["assignedNumber"]<100:
    assigned_number_text+="0"
    if api_response["assignedNumber"]<10:
        assigned_number_text+="0"

assigned_number_text+=str(api_response["assignedNumber"])
log_this("Displaying assigned number on screen: " + assigned_number_text)
display_assigned_number_on_screen(assigned_number_text, local_version)


# #########################################################
# Done!
# #########################################################

log_this("FIN")