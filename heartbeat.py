import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
from os import path, system
from time import sleep
import requests

def serialize(things):
    string = "{"
    is_first = True
    for key in things:
        if  not is_first:
            string += ","
        is_first = False
        string += '"'
        string += key
        string += '"'
        string += ":"
        string += '"'
        string += things[key]
        string += '"'
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

resp = None
URL = "https://envirosaurus.lskysd.ca/Heartbeat"
my_dict = {"deviceSerialNumber":get_serial(),"deviceModel":get_model()}
disp = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
disp.begin()
wait = Image.new('RGB', (disp.width, disp.height), color="Black")
ImageDraw.Draw(wait).text((0,15),"Updating", font=ImageFont.truetype(UserFont, 40), fill="White")
disp.display(wait)
img = Image.new('RGB', (disp.width, disp.height), color="Black")

print(serialize(my_dict))

#with requests.post(URL,data=serialize(my_dict),headers={"Content-Type":"application/json"}) as r:
#    if r.ok:
#        resp = r.json
#    else:
#        #put logging here
#        print(r.json)
#        raise Exception("logs")

#if not path.exists(".dnr"):
#    with open(".dnr","w") as f:
#        f.write("")
#    with open("/etc/hostname","w") as f:
#        f.write("Eap"+str(resp["assignedNumber"]))
#    #with open("version", "w") as f:
#        #f.write(resp["versionNumber"])
#    system("reboot")

#with open("version","r") as f:
    #version = f.readline().strip()

#if resp["versionNumber"] != version:
    #system("git pull EasyAsPi-Pi")
    #with open("version","w") as f:
        #f.write(resp["versionNumber"])
    #system("reboot")

#ImageDraw.Draw(img).text((0,-13),str(resp["assignedNumber"]), font=ImageFont.truetype(UserFont, 94), fill="White")