#Program to read different plant data (soil humidity, light, temperature) from a#plant using sensors connected to a Raspberry Pi
#The data is then inserted into a Sqlite database on the Raspberry. The database#is created within the code if it does not yet exist
#Date: 7.8.2023
#Author: Amalie Wilke
#Code for sensors taken (and expanded on) from ladyada for Adafruit Industries
#Connection for Soil Sensor and Tempearture: I2C

from time import time, sleep, strftime
from datetime import datetime

import board

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

def create_connection(irrigation_db):
    """creates a database connection to a SQLIte database """
    conn=None

    try:
        conn=sqlite3.connect("irrigation_db")
        print(sqlite3.version)
        print("Database created")

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

    except Error as e:
         print(e)
    finally:
        if conn:
            conn.close()

if __name__=='__main__':
    create_connection(r"/home/molly/Desktop")

#defining SQLite parameters for quicker coding

    while True:
        
        try:
            conn=sqlite3.connect("irrigation_db")
            cursor=conn.cursor()
            print("Database exists, SQLITE connection open)")
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
            sleep(120)

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