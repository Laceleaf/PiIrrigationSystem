#Python code using flask to display most current measurement values from our database
#on our website
#Amalie Wilke

from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
import io

from flask import Flask, render_template, send_file, make_response, request
app=Flask(__name__)
import sqlite3

#get most current data from database irrigation_db
def currentData():
	conn=sqlite3.connect("irrigation_db")
	curs=conn.cursor()
	for row in curs.execute("SELECT * FROM sensordata ORDER BY measured_at DESC LIMIT 1"):
		measured=str(row[5])
		temp=row[3]
		light=row[4]
		soil=row[2]
	conn.close()
	return temp, light, measured, soil
	
#get all data from database
def getAllData(num):
	conn=sqlite3.connect("irrigation_db")
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
		
#main for webpage, displays current temperature, light and soil moisture
@app.route("/")
def index():
	temp, light, measured, soil=currentData()
	htmlData={
	'time':measured,
	'temp': temp,
	'light': light,
	'soil': soil
	}
	
	return render_template('index.html', **htmlData)

#gets needed values to page
#@app.route("/", methods=['POST'])
#def datapost():
#	plotnumber=50
#	plotnumber=int (request.form['plotnumber']
	
#plots soil moisture
@app.route('/plot/soil')
def plot_soil():
	times, temps, soils, lights=getAllData(20)
	yaxis=soils
	fig=Figure()
	axis=fig.add_subplot(1, 1, 1)
	axis.set_title("Soil Moisture")
	axis.set_xlabel("Time")
	axis.grid(True)
	xs=times
	axis.plot(xs, yaxis)
	canvas=FigureCanvas(fig)
	output=io.BytesIO()
	canvas.print_png(output)
	response=make_response(output.getvalue())
	response.mimetype='image/png'
	return response	
	
if __name__=="__main__":
	app.run(host='0.0.0.0', port=80, debug=False)
	print("Is this working?")
