#LCD Display - the most annoying cable connected pieces of them all

from RPLCD import CharLCD
import RPi.GPIO as GPIO

import time
import sqlite3

#We are trying 4 bit mode so only use LCD pins D4 to D6 (in that order in array
lcd=CharLCD(cols=16, rows=2, pin_rs=37, pin_e=35, pins_data=[33, 31, 29, 23], numbering_mode=GPIO.BOARD)
lcd.write_string("Hello, Test")

def currentData():
    conn=sqlite3.connect("irrigation_db")
    curs=conn.cursor()
    for row in curs.execute("SELECT * FROM sensordata ORDER BY measured_at DESC LIMIT 1"):
        temp=round(row[3], 2)
        light=row[4]
        soil=row[2]
    conn.close()
    return temp, light, soil


if __name__=='__main__':
    lcd.clear()
    lcd.write_string("Test")
    time.sleep(4)
    lcd.clear()
    time.sleep(2)
    lcd.write_string("Test 2")
    lcd.clear()
    time.sleep(4)

    while True:
        temp, light, soil=currentData()
        #all of a sudden, we are back in C code, but guess how long it took to figure that out :|
        lcd.write_string("Soil:")
                # %i"
                #% soil)
        lcd.crlf()
        lcd.write_string("Temp: %f " % temp)
        time.sleep(900)
        lcd.clear()

