#basic Flask webpage to display plants in Sqlite database and the sensor values attached to them
#Amalie Wilke
#8.9.2023

from flask import Flask, render_template, send_file, make_response, request
from matplotlib.figure import Figure
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas

import io

import sqlite3

app = Flask(__name__, template_folder='templates', static_folder='static')


sqlite_select_WHERE="""SELECT * FROM sensordata WHERE plant_id= ?"""
sqlite_select_WHERE_plantname="""SELECT plant_id FROM planttable WHERE plant_name= ?"""

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
		temp=float(temp)
		light=float(light)
		soil=int(soil)
		
		conn.close()
		
		return measured, temp, light, soil
		
	else:
		print("Something went wrong querying data")
		return None

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
plant_type_images={
	'1': 'tomato.png',
	'2': 'basil.png'
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
	'plant_type_images': plant_type_images
	}
	

	return render_template('indexBoot.html', **htmlData) #looks for index.html folder in templates folder
	
@app.route('/about')
def about():
	return render_template('about.html')
	
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
	plantID_str=request.form.get('plantID')
	
	#if plantID_str and plantID_str.isdigit():
	
	#plantID=int(plantID_str)
	limit=20
	#times, temps, soils, lights=getAllData(30) #getPlantData(limit, plant_id)
	times,temps, soils, lights=getPlantData(20, (1,))
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
		
	
@app.route('/plant/<string:plant_name>')
def plant_detail(plant_name):
	conn=sqlite3.connect("/home/molly/irrigation_db")
	curs=conn.cursor()
	curs.execute(sqlite_select_WHERE_plantname, (plant_name,))
	plantID=curs.fetchone()
	getPlantData(20, plantID)
	
	#html
	
	return render_template('plant.html', plant_name=plant_name, plant_id=plantID)

if __name__=='__main__':
	app.run(host='169.254.170.93', port=5000, debug=True)
	
