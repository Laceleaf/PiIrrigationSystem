# PiIrrigationSystem

Irrigation System Overview:

![abstraktSystem](https://github.com/Laceleaf/PiIrrigationSystem/assets/76946697/53d44395-61b7-42f7-ac38-ee0c78f6cbe9)

Irrigation System Code Structure:

![software](https://github.com/Laceleaf/PiIrrigationSystem/assets/76946697/3225db8a-47c4-420f-a126-79c661c2db2c)

Software Guide: 

Raspberry Pi Module 4 B with Raspberry Pi OS (32-bit), Version 11 Bullseye 
Python-Version: 3.9.2 

Python Modules needed: 
1. Adafruit CircuitPython 
2. Adafruit CircuitPython seesaw
3. Blinka 
4. SQLlite3 
5. Flask 
6. Adafruit_CircuitPython_TSL2591 
7. Adafruit_CircuitPython_SHT4x 
8. Picamera (should be installed but check) 

Code Execution: 

With time and changes to code, the names in the python scripts shown in the code structure diagram have changed slightly.
To execute the system, run the script in following order via Raspberry Pi terminal (except when a path is specified):

0. Not completely necessary but recommended to have a plant in database to work with:
   python3 plantprofiles.py
   IT IS NOT recommended to change the database name because it is referenced in the different scripts but you will have to
   change your database path in the method create_connection()
1. python3 irrigation.py
   Again, please keep the database name but the path must be adapted to your own system
2. python3 wateringLoop.py
   script runs in loop but can be interrupted by keyboard interrupt (sometimes it needs to be done twice)
3. Switch to the directory web and then execute the script with sudo:
   sudo python3 irrigation_web.py

