import logging
logging.basicConfig(filename = "/var/log/EasyAsPi",level = logging.DEBUG, format = "%(asctime)s:%(levelname)s:on line %(lineno)d:%(message)s")
logging.debug("Imported logging")
logging.debug("Importing gpiozero")
import gpiozero
logging.debug("gpiozero Imported")
logging.debug("importing requests")
import requests
logging.debug("requests imported")
logging.debug("importing bme280")
from bme280 import BME280
logging.debug("bme280 imported")
logging.debug("importing ltr559")
import ltr559
logging.debug("ltr559 imported")
logging.debug("importing gas")
from enviroplus import gas
logging.debug("gas imported")
logging.debug("creating the temperature adjustment")
temp_compensate = 1.45
logging.debug("temperature adjustment created")
logging.debug("assigning the URL")
URL = "https://envirosaurus.lskysd.ca/SensorReading"
logging.debug("URL assigned")

def serialize(things):
    logging.debug("Begin serializing")
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
    logging.debug("end serializing")
    return string
def get_serial():
    logging.info("fetching serial number")
    logging.debug("opening cpuinfo file as read")
    with open("/proc/cpuinfo","r") as f:
        logging.debug("cpuinfo file opened as read")
        logging.debug("reading lines")
        for line in f:
            logging.debug("Checking if line starts with 'Serial'")
            if line[0:6]=="Serial":
                logging.debug("Line began with 'Serial'")
                logging.debug("returning characters 10 to -1")
                return line[10:-1]
logging.debug("creating empty dictionary")
my_dict = {}
logging.debug("created empty dictionary")
logging.debug("creating object for temperature, pressure and humidity sensor")
tph = BME280()
logging.debug("object for temperature, pressure and humidity sensor created")
logging.debug("Creating light sensor object")
light = ltr559.LTR559()
logging.debug("crerated object for light sensor")

logging.info("reading temperature, pressure and humidity")
logging.debug("updating tph sensor")
tph.update_sensor()
logging.debug("tph sensor updated")
logging.debug("priming temperature")
temp_primer = tph.temperature
logging.debug("primed temperature")
logging.debug("primning pressure")
pres_primer = tph.pressure
logging.debug("pressure primed")
logging.debug("priming humidity")
hum_primer = tph.humidity
logging.debug("humidity primed")
logging.debug("reading humidity into dictionary")
my_dict["humidityPercent"] = tph.humidity
logging.debug("humidity read into dictionary")
logging.debug("reading pressure into dictionary")
my_dict["pressure"] = tph.pressure
logging.debug("pressure read into dictionary")
logging.debug("reading temperature into dictionary")
my_dict["temperatureCelsius"] = tph.temperature
logging.debug("temperature read into dictionary")
logging.debug("looping until no values match the primers")
while temp_primer==my_dict["temperatureCelsius"]or pres_primer==my_dict["pressure"]or hum_primer==my_dict["humidityPercent"]:
    logging.debug("start of loop")
    logging.debug("updating tph sensor")
    tph.update_sensor()
    logging.debug("tph sensor updated")
    logging.debug("reading humidity")
    my_dict["humidityPercent"] = tph.humidity
    logging.debug("humidity read")
    logging.debug("reading pressure")
    my_dict["pressure"] = tph.pressure
    logging.debug("pressure read")
    logging.debug("reading temperature")
    my_dict["temperatureCelsius"] = tph.temperature
    logging.debug("tempreature read")
logging.info("reading cpu temperature")
my_dict["cpuTemperatureCelsius"] = gpiozero.CPUTemperature().temperature
logging.debug("cputemperature read")
logging.debug("compensating abient temperature for cpu temperature")
my_dict["temperatureCelsius"]=my_dict["temperatureCelsius"] - ((my_dict["cpuTemperatureCelsius"] - my_dict["temperatureCelsius"]) / temp_compensate)
logging.debug("abient temperature compensated")
logging.info("reading serial number into dictionary")
my_dict["deviceSerialNumber"] = get_serial().strip()
logging.debug("serial number read")
logging.info("reading light levels")
my_dict["lux"]=light.get_lux()
logging.debug("light levels read")
logging.info("reading gasses")
logging.debug("updating the gasses sensor")
gasses = gas.read_all()
logging.debug("reading the oxidising levels")
my_dict["oxidisingGasLevel"]=gasses.oxidising
logging.debug("oxidising levels read")
logging.debug("reading reducing levels")
my_dict["reducingGasLevel"]=gasses.reducing
logging.debug("reducing levels read")
logging.debug("reading nh3 levels")
my_dict["nH3Level"]=gasses.nh3
logging.debug("nh3 levels read")
logging.info("sending post request")
logging.info(requests.post(URL,data=serialize(my_dict),headers={"Content-Type":"application/json"}).json)