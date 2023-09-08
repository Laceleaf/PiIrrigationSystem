#Program to read different plant data (soil humidity, light, temperature) from a#plant using sensors connected to a Raspberry Pi
#The data is then inserted into a Sqlite database on the Raspberry. The database#is created within the code if it does not yet exist
#Date: 7.8.2023
#Author: Amalie Wilke
#Code for sensors taken (and expanded on) from ladyada for Adafruit Industries
#Connection for Soil Sensor and Tempearture: I2C

from time import time, sleep, strftime
from datetime import datetime

import board
import digitalio

#LCD Display library
from RPLCD import CharLCD
import RPi.GPIO as GPIO

import adafruit_sht4x
import adafruit_tsl2591

from adafruit_seesaw.seesaw import Seesaw


import sqlite3
from sqlite3 import Error

#board.SCL and board.SDA to use the built-in STEMMA QT connector
i2c_bus=board=board.I2C()

#soil sensor
ss=Seesaw(i2c_bus, addr=0x36)
#light sensor
ls=adafruit_tsl2591.TSL2591(i2c_bus)

#defines format of LCD (here 16x2)
lcd_columns=16
lcd_rows=2

#initiating pins for LCD display
#4 bit mode so only LCD pins D4 to D7 are in use (same order as here in array)
#I first used gpio.board mode in which the phyiscal pin numbers were used but had to switch to BCM (the gpio numbering)
#BOARD numbers: RS pin: 37, e pin: 36, D4:D7 - 33, 31, 29, 23
#BCM numbers using pinout command: rs: 26, e: 16, D4:27 - 13, 6, 5, 11
lcd=CharLCD(cols=lcd_columns, rows=lcd_rows, pin_rs=26, pin_e=16, pins_data=[13, 6, 5, 11], numbering_mode=GPIO.BCM)
#above numbering is used as I have had error responses not knowing which numbering format I chose (here I use phyiscal pin position)

#BOARD Mode for LCD
#lcd=CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23],numbering_mode= GPIO.BOARD)

#initializing LCD screen when first started - static
lcd.write_string("Boot Up Screen")

def create_connection(irrigation_db):
    """creates a database connection to a SQLIte database """
    conn=None

    try:
        conn=sqlite3.connect("irrigation_db")
        print(sqlite3.version)
        print("Database created")

#Creates Plant Table Database
        conn.execute('''
        CREATE TABLE IF NOT EXISTS planttable
        ([plant_id] INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
        [plant_type] INTEGER,
        [soil_sensor] INTEGER,
        [plant_name] TEXT,
        [created_at] TEXT,
        [watered] INTEGER,
        FOREIGN KEY (plant_type) 
            REFERENCES plantprofile (plant_type))
        ''')
#Creates Plant Profile Database
        conn.execute('''
        CREATE TABLE IF NOT EXISTS plantprofile
        ([plant_type] INTEGER NOT NULL UNIQUE PRIMARY KEY,
        [plant_species] TEXT,
        [watering_needs] TEXT,
        [soil_needs] TEXT,
        [ideal_soil_moisture] INTEGER,
        [ideal_light] INTEGER,
        [ideal_temperature] REAL)
        ''')

#Creates Sensor Data Database Table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS sensordata
        ([measurement_id] INTEGER NOT NULL UNIQUE PRIMARY KEY AUTOINCREMENT,
        [plant_id] INTEGER NOT NULL,
        [soil_capacitive] INTEGER,
        [temperature] REAL,
        [light] INTEGER,
        [measured_at] TEXT,
        FOREIGN KEY (plant_id)
            REFERENCES planttable (plant_id))
        ''')

#Creates Pump Database Table
        conn.execute('''
        CREATE TABLE IF NOT EXISTS pump
        ([pump_id] INTEGER NOT NULL UNIQUE PRIMARY KEY,
        [soil_sensor] INTEGER,
        FOREIGN KEY (soil_sensor)
            REFERENCES planttable (soil_sensor))
        ''')
    
    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    create_connection(r"/home/molly/Desktop")
    
    
#Create 
#defining SQLite parameters for quicker coding
    lcd.clear()
    lcd.message="Test"
    while True:
        
        try:
            conn=sqlite3.connect("irrigation_db")
            cursor=conn.cursor()
            lcd.clear()
            lcd.write_string("Loop")
            touch=ss.moisture_read()
            temp=ss.get_temp()
            ts=adafruit_sht4x.SHT4x(i2c_bus)
            tempts=ts.temperature
            lux=ls.lux
            print("Temperature:" +str(tempts))
            print("Moisture:" +str(touch))
            print("Light (lux): {0}".format(ls.lux))
            taken=datetime.now()
            takenconvert=taken.strftime("%d-%m-%Y %H:%M:%S")
            
            sqlite_insert="""INSERT INTO sensordata (plant_id, soil_capacitive,temperature,light,  measured_at) VALUES (?, ?, ?, ?,  ?);"""

            sensordata=(1, touch,tempts,lux, takenconvert)
            cursor.execute(sqlite_insert, sensordata)
            conn.commit()
            conn.close()
            sleep(900) #reads values each 15 minutes

        except sqlite3.Error as error:
            print("Error while connecting to db", error)
        
            #read moisture level through capacitive touch pad
            #touch=ss.moisture_read()
            #temp=ss.get_temp()
            #date=(time.strftime("%Y-%m-%d %H:%M:%S")

        finally:
            if conn:
                conn.close()
                print("Connection closed")
