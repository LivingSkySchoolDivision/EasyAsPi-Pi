import logging
logging.basicConfig(filename = "/var/log/EasyAsPi",level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:on line %(lineno)d:%(message)s")
logging.debug("Imported logging")
logging.debug("Importing display module")
import ST7735
logging.debug("Display module imported")
logging.debug("Importing image handler")
from PIL import Image, ImageDraw, ImageFont
logging.debug("Image handler imported")
logging.debug("importing font")
from fonts.ttf import RobotoMedium as UserFont
logging.debug("Font imported")
logging.debug("Importing OS resources")
from os import path, system
logging.debug("OSresources imported")
logging.debug("Importing requests")
import requests
logging.debug("Requests Imported")

def serialize(things):
    logging.debug("Began serializing")
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
    logging.debug("Finished Serializing")
    return string
def get_serial():
    logging.debug("Opening /proc/cpuinfo")
    with open("/proc/cpuinfo","r") as f:
        logging.debug("opened /proc/cpuinfo")
        logging.debug("Reading in line")
        for line in f:
            logging.debug("line read")
            logging.debug("Checking to see if line begins with 'Serial'")
            if line[0:6]=="Serial":
                logging.debug("It did")
                logging.debug("returning character 10 to character -1")
                return line[10:-1]
def get_model():
    logging.debug("Opening /proc/cpuinfo")
    with open("/proc/cpuinfo","r") as f:
        logging.debug("opened")
        logging.debug("reading in lines")
        for line in f:
            logging.debug("line read")
            logging.debug("Checking if line begins with 'model'")
            if line[0:5]=="Model":
                logging.debug("It did")
                logging.debug("returning charcters 9 to -1")
                return line[9:-1]

logging.debug("Creating display object")
disp = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
logging.debug("Display object created")
logging.debug("Initializing display")
disp.begin()
logging.debug("Display initialized")
logging.debug("Creating 'Updating' background")
wait = Image.new('RGB', (disp.width, disp.height), color="Black")
logging.debug("'Updating' background created")
logging.debug("Drawing 'Updating' text")
ImageDraw.Draw(wait).text((0,15),"Updating", font=ImageFont.truetype(UserFont, 40), fill="White")
logging.debug("'Updating' text Drawn")
logging.debug("Displaying 'Updating'")
disp.display(wait)
logging.debug("'Updating' displayed")
logging.debug("Creating reboot flag")
reboot = False
logging.debug("reboot flag created")
logging.debug("assigning URL")
URL = "https://envirosaurus.lskysd.ca/Heartbeat"
logging.debug("URL assigned")
logging.debug("Creating dictionary")
my_dict = {"deviceSerialNumber":get_serial(),"deviceModel":get_model()}
logging.debug("Dictionary created")
logging.debug("Creating background for image")
img = Image.new('RGB', (disp.width, disp.height), color="Black")
logging.debug("Background created")

logging.debug("Making post request now")
with requests.post(URL,data=serialize(my_dict),headers={"Content-Type":"application/json"}, timeout = 20) as r:
    logging.debug("Request made")
    logging.debug("Checking if it received a good response")
    if r.ok:
        logging.info("Received a good response")
        logging.debug("assigning response body to resp")
        resp = r.json()
        logging.debug("Response assigned")
    else:
        logging.error(f"Received bad response:{r.json()}")
        raise Exception("Received bad response")
logging.debug("Checking if version file exisits.")
if not path.exists("/home/pi/EasyAsPi-Pi/version"):
    logging.debug("It did not")
    logging.info("Editing hostname.")
    with open("/etc/hostname","w") as f:
        f.write("EaP"+my_dict["deviceSerialNumber"])
    logging.info("Creating version file")
    with open("/home/pi/EasyAsPi-Pi/version", "w") as f:
        f.write(resp["versionNumber"])
    logging.info("restarting")
    system("sudo reboot")
else:
    logging.info("Version file already existed")
logging.debug("Opening hostname file as read")
with open("/etc/hostname","r") as f:
    logging.debug("hostname file opened")
    logging.debug("reading, striping, and assigning the info from the file")
    hostname = f.readline().strip()
    logging.debug("file info read, stripped, and assigned")
logging.debug("checking if information is correct")
if hostname != f"EaP{get_serial()}":
    logging.debug("It was not")
    logging.info("changing hostname")
    logging.debug("openening hostname file as write")
    with open("/etc/hostname","w") as f:
        logging.debug("hostname file opened")
        logging.debug("writing to hostname file")
        f.write(f"EaP{get_serial()}")
        logging.debug("hostname file written")
    logging.debug("Raising the reboot flag for hostname")
    reboot = True
    logging.info("Raised the reboot flag for hostname")
else:
    logging.debug("host needn't be changed")
logging.info("Checking version")
logging.debug("opening version file")
with open("/home/pi/EasyAsPi-Pi/version","r") as f:
    logging.debug("version file opened")
    logging.debug("reading, stripping, and assigning info from version file")
    version = f.readline().strip()
    logging.debug("read, stripped, and a assigned info from version file")
logging.debug("checking if an update is available")
if resp["versionNumber"] != version:
    logging.debug("An update is available")
    logging.info("Performing git pull")
    system("git pull")
    logging.debug("Git Pull performed")
    logging.info("Updating version number")
    logging.debug("opening version file as write")
    with open("/home/pi/EasyAsPi-Pi/version","w") as f:
        logging.debug("version file opened as write")
        logging.debug("writing version number")
        f.write(resp["versionNumber"])
        logging.debug("version number written")
    logging.debug("raising reboot flag")
    reboot = True
    logging.info("Raised the reboot flag for version")
logging.debug("Checking if reboot flag is raised")
if reboot:
    logging.debug("reboot flag was raised")
    logging.info("Rebooting due to flag being raised")
    system("sudo reboot")
    logging.error("Failed to reboot do to raised flag")
logging.info("adding leading 0s to assigned number.")
logging.debug("creating empty string")
text_str = ""
logging.debug("empty string created")
logging.debug("Checking to to see if the number is less than 100")
if resp["assignedNumber"]<100:
    logging.debug("number is less than 100")
    logging.debug("prepending 0")
    text_str+="0"
    logging.debug("0 prepended")
    logging.debug("checking if the number is less than 10")
    if resp["assignedNumber"]<10:
        logging.debug("the number is less than 10")
        logging.debug("prepending 0")
        text_str+="0"
        logging.debug("0 prepended")
    else:
        logging.debug("number greater than or equal to 10, no 0 required")
else:
    logging.debug("number greater than or equal to 100, no 0s required")
logging.debug("appending assigned number to leading 0s")
text_str+=str(resp["assignedNumber"])
logging.debug("assigned number appended")
logging.info("Drawing assigned number on the image")
ImageDraw.Draw(img).text((0,-13),text_str, font=ImageFont.truetype(UserFont, 94), fill="White")
logging.debug("number drawn on screen")
logging.info("Displaying assigned number on screen")
disp.display(img)
logging.debug("image displayed")
logging.info("FIN")