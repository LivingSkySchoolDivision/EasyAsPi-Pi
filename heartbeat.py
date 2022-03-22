import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
from os import path, system
import requests
import logging

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
    with open("/proc/cpuinfo","r") as f:
        for line in f:
            if line[0:6]=="Serial":
                return line[10:26]
def get_model():
    with open("/proc/cpuinfo","r") as f:
        for line in f:
            if line[0:5]=="Model":
                return line[9:-1]


disp = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
disp.begin()
wait = Image.new('RGB', (disp.width, disp.height), color="Black")
ImageDraw.Draw(wait).text((0,15),"Updating", font=ImageFont.truetype(UserFont, 40), fill="White")
disp.display(wait)
logging.basicConfig(filename = "/var/log/EasyAsPi",level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:on line %(lineno)d:%(message)s")
reboot = False
resp = None
URL = "https://envirosaurus.lskysd.ca/Heartbeat"
my_dict = {"deviceSerialNumber":get_serial(),"deviceModel":get_model()}
img = Image.new('RGB', (disp.width, disp.height), color="Black")

logging.debug("Making post request now")
with requests.post(URL,data=serialize(my_dict),headers={"Content-Type":"application/json"}) as r:
    if r.ok:
        logging.info("Received a good response")
        resp = r.json()
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

logging.debug("Checking hostname")
with open("/etc/hostname","r") as f:
    hostname = f.readline().strip()
if hostname != f"EaP{get_serial()}":
    logging.info("changing hostname")
    with open("/etc/hostname","w") as f:
        f.write(f"EaP{get_serial()}")
    reboot = True
    logging.info("Raised the reboot flag for hostname")

logging.debug("Checking version")
with open("/home/pi/EasyAsPi-Pi/version","r") as f:
    version = f.readline().strip()
if resp["versionNumber"] != version:
    logging.info("Performing git pull")
    system("git pull")
    logging.info("Updating version number")
    with open("/home/pi/EasyAsPi-Pi/version","w") as f:
        f.write(resp["versionNumber"])
    reboot = True
    logging.info("Raised the reboot flag for version")

if reboot:
    logging.info("Rebooting due to flag being raised")
    system("sudo reboot")
logging.info("adding leading 0s to assigned number.")
text_str = ""
if resp["assignedNumber"]<100:
    text_str+="0"
    if resp["assignedNumber"]<10:
        text_str+="0"
text_str+=str(resp["assignedNumber"])
logging.info("Drawing assigned number on the image")
ImageDraw.Draw(img).text((0,-13),text_str, font=ImageFont.truetype(UserFont, 94), fill="White")
logging.info("Displaying assigned number on screen")
disp.display(img)
logging.info("FIN")