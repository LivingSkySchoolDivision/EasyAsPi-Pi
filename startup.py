import ST7735
from PIL import Image, ImageDraw, ImageFont
from fonts.ttf import RobotoMedium as UserFont
from os import path, system
from time import sleep
first = False
disp = ST7735.ST7735(port=0,cs=1,dc=9,backlight=12,rotation=90,spi_speed_hz=10000000)
disp.begin()
wait = Image.new('RGB', (disp.width, disp.height), color="Black")
ImageDraw.Draw(wait).multiline_text((15,-5),"Please\nWait", font=ImageFont.truetype(UserFont, 42), fill="White", align="center")
img = Image.new('RGB', (disp.width, disp.height), color="Black")
if not path.exists("/home/pi/ID"):
    disp.display(wait)
    first = True
    while not path.exists("/home/pi/ID"):
        sleep(2)
with open("/home/pi/ID","r") as f:
    id_str = f.readline().strip()
    ImageDraw.Draw(img).text((0,-13),id_str, font=ImageFont.truetype(UserFont, 94), fill="White")
if first:
    with open("/etc/hostname","w") as f:
        f.write(f"EaP{id_str}")
    system("reboot")
#Check for updates here
disp.display(img)