#Creates plant profiles and test plants for the SQLite DB
#author: Amalie Wilke

from time import time, sleep, strftime
from datetime import datetime
import sqlite3


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
	conn=sqlite3.connect("irrigation_db")
	cursor=conn.cursor()
	
	#Test Plant Table Profile
	created=datetime.now()
	convert=created.strftime("%d-%m-%Y %H:%M:%S")
	#testplant=(1, 1, "Sola", convert, 0)
	testplant=(2, 2, "Basil", convert, 0)
	
	#Tomato Profil
	tomato_profile = (1, "Tomate", "Hoch", "nährstoffreich", 700, 10, 26)
	#Basilikum Profil
	basil_profile = (2, "Basilikum", "Hoch", "locker", 800, 15, 24)
	
	insert_planttable="INSERT INTO planttable (plant_type, soil_sensor, plant_name, created_at, watered) VALUES (?, ?, ?, ?, ?)"
	insert_profile="""INSERT INTO plantprofile (plant_type, plant_species, watering_needs, soil_needs, ideal_soil_moisture, ideal_light, ideal_temperature) VALUES (?, ?, ?, ?, ?, ?, ?);"""
	cursor.execute(insert_planttable, testplant)
	cursor.execute(insert_profile, basil_profile) 
	conn.commit()
	print("Test plant created")
	
	conn.close()
