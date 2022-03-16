import gpiozero
import requests
from bme280 import BME280
import ltr559
from enviroplus import gas
from os import path
temp_compensate = 1.45

URL = "https://envirosaurus.lskysd.ca/SensorReading"

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
        if type(things[key]) == str:
            string += '"'
            string += things[key]
            string += '"'
        elif type(things[key]) == bool:
            if things[key]:
                string += "true"
            else:
                string += "false"
        else:
            string += str(things[key])
        
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

my_dict = {}
tph = BME280()
light = ltr559.LTR559()

tph.update_sensor()
temp_primer = tph.temperature
pres_primer = tph.pressure
hum_primer = tph.humidity
my_dict["humidityPercent"] = tph.humidity
my_dict["pressure"] = tph.pressure
my_dict["temperatureCelsius"] = tph.temperature
while temp_primer==my_dict["temperatureCelsius"]or pres_primer==my_dict["pressure"]or hum_primer==my_dict["humidityPercent"]:
    tph.update_sensor()
    my_dict["humidityPercent"] = tph.humidity
    my_dict["pressure"] = tph.pressure
    my_dict["temperatureCelsius"] = tph.temperature
my_dict["cpuTemperatureCelsius"] = gpiozero.CPUTemperature().temperature
my_dict["temperatureCelsius"]=my_dict["temperatureCelsius"] - ((my_dict["cpuTemperatureCelsius"] - my_dict["temperatureCelsius"]) / temp_compensate)
my_dict["deviceModel"] = get_model()
my_dict["deviceSerialNumber"] = get_serial().strip()
my_dict["lux"]=light.get_lux()

gasses = gas.read_all()

my_dict["oxidisingGasLevel"]=gasses.oxidising
my_dict["reducingGasLevel"]=gasses.reducing
my_dict["nH3Level"]=gasses.nh3

with requests.post(URL,data=serialize(my_dict),headers={"Content-Type":"application/json"}) as r:
    if not path.exists("ID"):
        string = ""
        if r.json()["assignedNumber"]-99<1:
            string = "0"
            if r.json()["assignedNumber"]-9<1:
                string += "0"
        string += str(r.json()["assignedNumber"])
        with open("ID","w") as f:
            f.write(string)
    if r.ok:
        print("┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼████████┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼░███░░░░░██░┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼░██░░░░░░░░█░┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼░██░░░░░░░░░█░┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼██░░░░░░░░░██┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼░█░░░░░░░░░██┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼██░░░░░░░░██░┼┼┼\n┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼┼░█░░░░░░░░██░┼┼┼┼\n┼┼┼┼┼┼┼┼┼░█████░░░┼┼┼┼┼░█░░░░░░░░█░┼┼┼┼┼\n┼┼┼┼┼┼┼░█████████████░┼██░░░░░░░█░┼┼┼┼┼┼\n┼┼┼┼┼┼░██░░░░░░██░░█████░░░░░░░██┼┼┼┼┼┼┼\n┼┼┼┼┼┼██░░░░░░░░░█░░░░░██░░░░░░██┼┼┼┼┼┼┼\n┼┼┼┼░███░░░░░░░░░░█░░░░░░░░░░░░██┼┼┼┼┼┼┼\n┼┼┼░██░░█░░░░░░░░░░█░░░█░░░░░░░░█░┼┼┼┼┼┼\n┼┼░██░░░██░░░░░░░░░██░██░░░░░░░░░█░┼┼┼┼┼\n┼┼░██░░░███░░░░░░░░░█░░░██░░░░░░░██┼┼┼┼┼\n┼┼┼░█░░░░░░██░░░░░░░░░░░░█░░░░░░░░█┼┼┼┼┼\n┼┼░███░░░░░░██░░░░░░░░░░░██░░░░░░░██░┼┼┼\n┼░██░██░░░░░░███░██░░░░░██░░░░░░░░████░┼\n┼██░░░██░░░░░░░░█████████░░░░░░░░░█░░██┼\n┼██░░░░██░░░░░░░░░░░░░░██░░░░░░░░██░░░█┼\n┼┼█░░░░░███░░░░░░░░░░░░█░█░░░░░░██░░░░█┼\n┼░██░░░░░░███████░░░░███░░██░░░██░░░░██┼\n┼████░░░░░░░░█████████░░░░░░█░░░░░░░░█░┼\n┼██░██░░░░░░░░░░░░░░░█░░░░░░░░░░░░░░██┼┼\n┼┼██░░███░░░░█░░░░░░██░░░░░░░░░░░░░██░┼┼\n┼┼░██░░███████░█████░░░░░░██░░░░░░██░┼┼┼\n┼┼┼┼███░░░░█░░█░██░░░░░████░░░░░███░┼┼┼┼\n┼┼┼┼┼░███████████████████████████░┼┼┼┼┼┼\n┼┼┼┼┼┼┼┼░░░░░░░░░░░░░░░░░░░░░░░░┼┼┼┼┼┼┼┼")