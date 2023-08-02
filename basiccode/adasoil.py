#2021 ladyada for Adafruit Industries
#Expanded by Amalie Wilke, 27.7.23
#Adafruit Soil Sensor using I2C connection on Raspberry Pi

from time import time, sleep, strftime

import board

from adafruit_seesaw.seesaw import Seesaw

i2c_bus=board.I2C() #uses board.SCL and board.SDA
#i2c_bus =board.STEMMA_I2C() #for using the built-in STEMMA QT connector on a mictrocontroller

ss=Seesaw(i2c_bus, addr=0x36)

with open("/home/molly/test.csv", "a") as log:
    while True:
    #read moisture level trhough capacitive touch pad
        touch=ss.moisture_read()

    #read temperature from temperature sensor (although values seem incorrect)
        temp=ss.get_temp()
        print("temp:" +str(temp) + " moisture:" +str(touch))
        log.write("{0}, {1}\n".format(strftime("%Y-%m-%d %H:%M:%S"), str(touch)))
        sleep(60) #read values and log them every 1 minute
