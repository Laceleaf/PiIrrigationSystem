#basic Flask webpage to display plants in Sqlite database and the sensor values attached to them
#Amalie Wilke
#8.9.2023

from flask import Flask, render_template, send_file, make_response, request, redirect, url_for, request
from matplotlib.figure import Figure
import base64
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

from time import time
from datetime import datetime

#from camera import VideoCamera
import os

import io

import sqlite3

#camera
#pi_camera=VideoCamera(flip=False) #flips camera

app = Flask(__name__, template_folder='templates', static_folder='static')


sqlite_select_WHERE="""SELECT * FROM sensordata WHERE plant_id= ?"""
sqlite_select_WHERE_plantname="""SELECT plant_id FROM planttable WHERE plant_name= ?"""
sqlite_insert_planttable="""INSERT INTO planttable (plant_type, soil_sensor, plant_name, created_at, watered) VALUES (?, ? ,?, ?, ?)"""


#def gen(camera):
#	#ger camera frame
#	while True:
#		frame=camera.get_frame()
#		yield(b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
		

#get most current data from database irrigation_db
def currentData():
	conn=sqlite3.connect("/home/molly/irrigation_db")
	cursor=conn.cursor()
	cursor.execute("SELECT measured_at, temperature, light, soil_capacitive FROM sensordata ORDER BY measurement_id DESC LIMIT 1")
	result=cursor.fetchall()
	
	if result: 
		
		for row in result:
			print(row)
		
		measured, temp, light, soil=result[0]
		measured=str(measured)
		print(measured)
		temp=round(float(temp), 1)
		light=round(float(light), 1)
		soil=int(soil)
		
		conn.close()
		
		return measured, temp, light, soil
		
	else:
		print("Something went wrong querying data")
		return None
		
#takes values of last 7 days and calculates averages of soil moisture, light and temp
def averageData(plantID):
	#15 minute intervals of measuring: (1440 min in day/15)x7
	values=int((1440/15)*7)
	times, temp, soil, light=getPlantData(values, (plantID,))
	
	if soil:
		avSoil=round(sum(soil)/len(soil), 2)
	
	else:
		avSoil=0
	#avLight=sum(light)/len(light)
	
	#if temp:
	#	avTemp=sum(temp)/len(temp)
	
	#else:
	#	avTemp=0
	
	
	return avSoil#, avLight, avTemp
	
	
	
#get all data from database
def getAllData(num):
	conn=sqlite3.connect("/home/molly/irrigation_db")
	curs=conn.cursor()
	#maybe prettier way here to select how much values to display, currently last 20
	curs.execute("SELECT * FROM sensordata ORDER BY measured_at DESC LIMIT 20")
	allData=curs.fetchall()
	#initialize empty arrays for flood of data
	allTime=[]
	allTemp=[]
	allSoil=[]
	allLight=[]
	
	conn.close()
	
	#reversed(): reverse of given sequence of data above, returned as list
	for row in reversed(allData):
		allTime.append(row[5])
		allTemp.append(row[3])
		allSoil.append(row[2])
		allLight.append(row[4])
		
	return allTime, allTemp, allSoil, allLight

#get sensor data from database from specifi plant using their ID	
def getPlantData(num, plantID):
	#plantID=(plantID,)
	conn=sqlite3.connect("/home/molly/irrigation_db")
	curs=conn.cursor()
	#maybe prettier way here to select how much values to display, currently last 20
	curs.execute(sqlite_select_WHERE, plantID)
	allData=curs.fetchmany(num)
	#initialize empty arrays for flood of data
	allTime=[]
	allTemp=[]
	allSoil=[]
	allLight=[]
	
	conn.close()
	
	#reversed(): reverse of given sequence of data above, returned as list
	for row in reversed(allData):
		allTime.append(row[5])
		allTemp.append(row[3])
		allSoil.append(row[2])
		allLight.append(row[4])
		
	return allTime, allTemp, allSoil, allLight

#Dictionary that maps plant types from database (ID 1..) to icons of their type
plant_type_text={
	1: 'Tomate',
	2: 'Basilikum'
	}
	

#Dictionary that maps plant types from database (ID 1..) to their species as text
plant_type_images={
	1: 'tomatoes.png',
	2: 'basil.png'
	}

#Dictionary that maps plant types from database (ID 1..) to their species as text
plant_status={
	1: 'wilt.png',
	2: 'overexposure.png',
	3: 'cold.png',
	4: 'happy.png'
	}
		
#retrieves all plants from planttable to display		
def get_plants():
	conn=sqlite3.connect("/home/molly/irrigation_db")
	curs=conn.cursor()
	curs.execute("SELECT plant_name, plant_type, plant_id FROM planttable ORDER BY plant_id ASC")
	plants=curs.fetchall()
	
	conn.close()
	
	for row in plants:
		print(row[0])

	return plants
	
	
@app.route('/')
def index(): #index view function to return result of calling render_template with index.html
	measured, temp, light, soil=currentData()
	plants=get_plants()
	htmlData={
	'time':measured,
	'temp':temp,
	'light':light,
	'soil': soil,
	'plants': plants,
	'plant_type_images': plant_type_images,
	'plant_type_text': plant_type_text
	}
	

	return render_template('indexBoot.html', **htmlData) #looks for index.html folder in templates folder
	
@app.route('/about')
def about():
	return render_template('about.html')

#@app.route('/videofeed')
#def video_feed():
#	return Response(gen(pi_camera),
#					mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/add_plant', methods=['Get', 'POST'])
def add_plant():
	
	if request.method=='POST':
		plant_type=request.form['plant_type']
		soil_sensor=request.form['soil_sensor']
		plant_name=request.form['plant_name']
		
		taken=datetime.now()
		takenconvert=taken.strftime("%d-%m-%Y %H:%M:%S")
		plantData=(plant_type, soil_sensor, plant_name, takenconvert, 0)
		conn=sqlite3.connect("/home/molly/irrigation_db")
		curs=conn.cursor()
		curs.execute(sqlite_insert_planttable, plantData)
		conn.commit()
		conn.close()
		
		return redirect(url_for('index'))


	return render_template('addPlant.html')


@app.route('/plant/<string:plant_name>')
def plant_detail(plant_name):
	conn=sqlite3.connect("/home/molly/irrigation_db")
	curs=conn.cursor()
	curs.execute(sqlite_select_WHERE_plantname, (plant_name,))
	plantID=curs.fetchone()
	plantInt=int(plantID[0])
	#getPlantData(20, plantID)
	
	#gets data from last 7 days, roughly:
	avSoil=averageData(plantInt)
	
	#collects all necessary data from fetched from database:
	times, temps, soils, lights=getPlantData(20, (plantInt,))
	
	#generates plots
	yaxis=soils
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Bodenfeuchte")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
	#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	soil_image=base64.b64encode(output.getvalue()).decode('utf-8')
	
	#generates plot for light exposure
	yaxis=lights
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Licht (in Lux)")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
	#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	light_image=base64.b64encode(output.getvalue()).decode('utf-8')
	
	#generates plot for temperature
	yaxis=temps
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Temperatur")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
	#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	temp_image=base64.b64encode(output.getvalue()).decode('utf-8')
	
	#html
	htmlData={
	'IDplant':plantInt,
	'plant_type_text': plant_type_text,
	'avSoil': avSoil,
	#'avLight': avLight,
	#'avTemp': avTemp,
	'soil_plot': soil_image,
	'light_plot': light_image,
	'temp_plot': temp_image
	}
	
	return render_template('plant.html', **htmlData, plant_name=plant_name, plant_id=plantID)

	
@app.route('/plot/soil')
def plot_soil():
	times, temps, soils, lights=getAllData(20)
	yaxis=soils
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Bodenfeuchte")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
	#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	response=make_response(output.getvalue())
	response.mimetype='image/png'
	return response	

@app.route('/plot', methods=['Get', 'POST'])
def plot_values(): 
	#plantID_str=request.form.get('plant_ID')
	numb=request.form['numb']
	
	#if plantID_str and plantID_str.isdigit():
	
	#plantID=int(plantID_str)
	limit=20
	#times, temps, soils, lights=getAllData(30) #getPlantData(limit, plant_id)
	times,temps, soils, lights=getPlantData(20, (numb,))
	yaxis=soils
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Bodenfeuchte")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
			#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	response=make_response(output.getvalue())
	response.mimetype='image/png'
	return response	
		
	#return "Invalid or missing Plant ID"
	
@app.route('/plot/light', methods=['Get', 'POST'])
def plot_light(): 
	plantID_str=request.form.get('plantID')
	
	#if plantID_str and plantID_str.isdigit():
	
	#plantID=int(plantID_str)
	limit=20
	#times, temps, soils, lights=getAllData(30) #getPlantData(limit, plant_id)
	times,temps, soils, lights=getPlantData(20, (1,))
	yaxis=lights
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Licht")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
			#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	response=make_response(output.getvalue())
	response.mimetype='image/png'
	return response	
		
	#return "Invalid or missing Plant ID"
	
@app.route('/plot/temp', methods=['Get', 'POST'])
def plot_temp(): 
	plantID_str=request.form.get('plantID')
	
	#if plantID_str and plantID_str.isdigit():
	
	#plantID=int(plantID_str)
	limit=20
	#times, temps, soils, lights=getAllData(30) #getPlantData(limit, plant_id)
	times,temps, soils, lights=getPlantData(20, (1,))
	yaxis=temps
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Temperatur")
	axis.set_xlabel("Uhrzeit")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	
			#Rotate the x-axis labels by 45 degrees
	axis.set_xticklabels(xs, rotation=45)
	
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	response=make_response(output.getvalue())
	response.mimetype='image/png'
	return response	
		
	#return "Invalid or missing Plant ID"
		
	


if __name__=='__main__':
	app.run(host='0.0.0.0', port=5000, debug=True)
	
