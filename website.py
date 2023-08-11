#Python code using flask to display most current measurement values from our database
#on our website
#Amalie Wilke

from flask import Flask, render_template, request
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
	
#main
@app.route("/")
def index():
	temp, light, measured, soil=currentData()
	htmlData={
	'time':measured,
	'temp': temp,
	'light': light,
	'soil': soil}
	
	return render_template('index.html', **htmlData)
	
if __name__=="__main__":
	app.run(host='0.0.0.0', port=80, debug=False)
	
	
