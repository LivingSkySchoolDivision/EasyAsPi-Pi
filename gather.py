import logging
logging.basicConfig(filename = "/var/log/EasyAsPi",level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:on line %(lineno)d:%(message)s")
import gpiozero
import requests
from bme280 import BME280
import ltr559
from enviroplus import gas
from os import path, system, getcwd

temp_compensate = 1.45

API_URL = "https://envirosaurus.lskysd.ca/SensorReading"

# #########################################################
# Function definitions and initialization stuff
# #########################################################

def log_this(text):
    print(text)
    logging.info(text)

def convert_to_json(obj):
    returned_json = "{"
    is_first = True
    for key in obj:
        if  not is_first:
            returned_json += ","
        is_first = False
        returned_json += '"'
        returned_json += key
        returned_json += '"'
        returned_json += ":"
        if type(obj[key]) == str:
            returned_json += '"'
            returned_json += obj[key]
            returned_json += '"'
        elif type(obj[key]) == bool:
            if obj[key]:
                returned_json += "true"
            else:
                returned_json += "false"
        else:
            returned_json += str(obj[key])
    returned_json += "}"
    return returned_json

def get_serial():
    with open("/proc/cpuinfo","r") as f:
        for line in f:
            if line[0:6]=="Serial":
                return line[10:-1].strip()

def get_version():
    with open(f"{path.dirname(__file__)}/version","r") as version_file:
        return version_file.readline().strip()

sensor_payload = {}

tph = BME280()
light = ltr559.LTR559()

# #########################################################
# Read temperature, pressure, and humidity data
# #########################################################

log_this("reading temperature, pressure and humidity")
tph.update_sensor()
temp_primer = tph.temperature
pres_primer = tph.pressure
hum_primer = tph.humidity
sensor_payload["humidityPercent"] = tph.humidity
sensor_payload["pressure"] = tph.pressure
sensor_payload["temperatureCelsius"] = tph.temperature
while temp_primer==sensor_payload["temperatureCelsius"]or pres_primer==sensor_payload["pressure"]or hum_primer==sensor_payload["humidityPercent"]:
    tph.update_sensor()
    sensor_payload["humidityPercent"] = tph.humidity
    sensor_payload["pressure"] = tph.pressure
    sensor_payload["temperatureCelsius"] = tph.temperature


# #########################################################
# Read CPU temp
# #########################################################

log_this("reading cpu temperature")
sensor_payload["cpuTemperatureCelsius"] = gpiozero.CPUTemperature().temperature
sensor_payload["temperatureCelsius"]=sensor_payload["temperatureCelsius"] - ((sensor_payload["cpuTemperatureCelsius"] - sensor_payload["temperatureCelsius"]) / temp_compensate)


# #########################################################
# Retrieve serial number
# #########################################################
log_this("reading serial number into dictionary")
sensor_payload["deviceSerialNumber"] = get_serial()

# #########################################################
# Read lux/light meter
# #########################################################

log_this("reading light levels")
sensor_payload["lux"]=light.get_lux()

# #########################################################
# Read gas sensors
# #########################################################

log_this("reading gasses")
gasses = gas.read_all()
sensor_payload["oxidisingGasLevel"]=gasses.oxidising
sensor_payload["reducingGasLevel"]=gasses.reducing
sensor_payload["nH3Level"]=gasses.nh3

# #########################################################
# Send this payload to the API
# #########################################################

log_this("sending post request")
log_this(requests.post(API_URL,data=convert_to_json(sensor_payload),headers={"Content-Type":"application/json"}, timeout = 20).json)