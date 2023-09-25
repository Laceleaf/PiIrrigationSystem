#Python script to set up a GPIO pin 21 on Raspberry Pi (using Broadcom numbering) to send signal to 
#water pump via a relay if most recent soil moisture in irrigation database is below ideal value
#Program runs on True loop but can be interrupted by keyboard interrupt
#author: Amalie Wilke

import RPi.GPIO as GPIO
import time
import sqlite3

channel=21

GPIO.setmode(GPIO.BCM)
GPIO.setup(channel, GPIO.OUT)

def motor_on(pin):
    GPIO.output(pin, GPIO.HIGH)

def motor_off(pin):
    GPIO.output(pin, GPIO.LOW)
   
db_path="irrigation_db"

sqlite_select="""SELECT plant_type FROM planttable WHERE plant_id = ?"""
sqlite_select_plantprofile="""SELECT ideal_soil_moisture FROM plantprofile WHERE plant_type = ?"""

#Selecting plant_id and soil_capacitive from sensor data
def retrieve_value(conn):
	cursor=conn.cursor()
	cursor.execute("SELECT plant_id, soil_capacitive FROM sensordata ORDER BY measurement_id DESC LIMIT 1")
	result=cursor.fetchall()
	
	if result: 
		
		for row in result:
			print(row)
		
		plant_id, soil_capacitive=result[0]
		plant_id=int(plant_id)
		print(plant_id)
		soil_capacitive=int(soil_capacitive)

		
		return plant_id, soil_capacitive
		
	else:
		print("Something went wrong querying data")
		return None
		
def compare_value(conn, plantID, soil_capacitive):
	
	cursor=conn.cursor()
	#cursor.execute() expects a tuple or dictionary to be passed, so we need to 
	#modify our integer plantID into a single element tuple
	cursor.execute(sqlite_select, (plantID,))
	#cursor.execute("SELECT plant_type FROM planttable WHERE plant_id = 1")
	result=cursor.fetchone()
	
	if result:
		plantType=result[0]
		plantType=int(plantType)
		print("Converted Plant Type:")
		print(plantType)
		cursor.execute(sqlite_select_plantprofile, (plantType,))
		ideal=cursor.fetchone()
			
		soil=ideal[0]
		soil=int(soil)
		print("Ideal Soil Moisture:")
		print(soil)
		
		if soil_capacitive < soil:
			try:
				motor_on(channel)
				time.sleep(5) #5 Seconds more appropriate than 10 seconds
				motor_off(channel)
				time.sleep(1)
				
			except KeyboardInterrupt:
				GPIO.cleanup()
				pass
		
	else:
		print("Plant ID not found in DB")
		
	
if __name__=='__main__':
	
	try:
	
		while True:
	
			conn=sqlite3.connect(db_path)
			
			result=retrieve_value(conn)

			plantID=int(result[0])
			actualSoil=int(result[1])
			print(actualSoil)
			
			compare_value(conn, plantID, actualSoil)
			
			conn.close()
			time.sleep(3600)
		
	except KeyboardInterrupt:
		try:
			conn.close()
		except NameError:
			pass
		finally:
			#reset GPIO
			GPIO.cleanup()
			print("Loop terminated by keyboard interrupt")
		
	
		
