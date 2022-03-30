# EasyAsPi-Pi
This code is for the _Easy As Pi_ project at Living Sky School division.

This project involves getting 300 Raspberry Pis to collect environmental data using Pimoroni Enviro+ modules, and to report that data back to a central system where that data can be displayed in a central manner, ideally on TV-sized displays, in map form.

# API and Frontend code and documentation
This repository exclusively contains code for this project that runs on the Raspberry Pi sensor devices - All other code, including for the API and web frontend, can be found in it's own repository here: https://github.com/LivingSkySchoolDivision/EasyAsPi

# Structure of this code

This repo contains two scripts:
 - __heartbeat.py__: Used to register the sensor device with the API, and check for updates
 - __gather.py__: Gathers data from sensors and submits that data to the API


# Installation
## Prerequisites
This code expects a Raspberry Pi Zero WH with a Pimoroni Enviro+ Air Quality pHAT.
This code is not written to work outside our own network, though it should work just fine with some minor modifications. 
This code expects that the corresponding API is running in your network, and is running at a specific address that is currently written in the python script. You may need to modify the script if you are running this in another environment.

To install prerequisites:
```
cd /opt
sudo git clone https://github.com/pimoroni/enviroplus-python
cd enviroplus-python
sudo ./install-bullseye.sh
reboot
```
You do not have to install the example code, when it prompts.
You must reboot your pi after you install this.

## Installation instructions
```
cd /opt
sudo git clone https://github.com/LivingSkySchoolDivision/EasyAsPi-Pi.git
```

Now add the following lines to your crontab:

```
@reboot python3 /opt/EasyAsPi-Pi/heartbeat.py
0 0 * * * sleep $((RANDOM \%18000)) && python3 /opt/EasyAsPi-Pi/heartbeat.py
0 12 * * * sleep $((RANDOM \%18000)) && python3 /opt/EasyAsPi-Pi/heartbeat.py
0 0 1 * * python3 /opt/EasyAsPi-Pi/heartbeat.py
*/5 * * * * python3 /opt/EasyAsPi-Pi/gather.py
```