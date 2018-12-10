#Nadav Miran - 308426048
#Barel Meir - 308275445
#intro video: https://drive.google.com/open?id=1nqE2BPErAsHMa3Gct4Kbu-CmCSlDnD9j
#example video: https://drive.google.com/open?id=1j0VKnplJdXyRbj9C8SpmqMMacNQ91UJq

import RPi.GPIO as GPIO
import time
import wiringpi
from time import sleep
import random
import Adafruit_GPIO.SPI as SPI
import Adafruit_MCP3008
import Adafruit_DHT
from mpu6050 import mpu6050


#Set up script to use the right pin configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

#MCP3008 setup
CLK = 18
MISO = 23
MOSI = 24
CS = 25
mcp = Adafruit_MCP3008.MCP3008(clk = CLK, cs = CS, miso = MISO, mosi = MOSI)

#gyro sensor setup
gyroSensor = mpu6050(0x68)

#game output setup
gpioSound = 5
Led_Array = [12,17,27,22] #red, yellow, green, blue
mapping = {0:(12,440), 1:(17,523),2:(27,659),3:(22,784)}

#sound setup
wiringpi.wiringPiSetupGpio()
wiringpi.softToneCreate(gpioSound)

roundList = []
roundListIterator = 0

#Set all the Led pins to outputs
for index in range(len(Led_Array)):
	GPIO.setup(Led_Array[index], GPIO.OUT)

def checkUserInput(index):
	global roundList
	global roundListIterator

	if(index != roundList[roundListIterator]):
		roundList = []
		roundListIterator = 0
		endRound()
	else:
		roundListIterator += 1
		if(roundListIterator == len(roundList)):
			addToList()
			roundListIterator = 0
	

#------------ color and sound event
def ledAndSound(index):
	#print("Enter at ", index)
	GPIO.output(Led_Array[index], 1)
	wiringpi.softToneWrite(gpioSound,mapping[index][1])
	time.sleep(0.5)
	wiringpi.softToneWrite(gpioSound,0)
	GPIO.output(Led_Array[index],0)

def startNewGame():
	sleep(1)
	startShow = [0,1,2,3,3,2,1,0]
	for i in startShow:
		ledAndSound(i)
		sleep(0.2)
	print("start!")
	sleep(1.5)
	addToList()

def endRound():
	print("End round")
	endShow = [0,0,1,1,2,2,3,3]
	for i in endShow:
		ledAndSound(i)
		sleep(0.2)
	print("end!")
	print("Starting a new round")
	startNewGame()

def addToList():
	global roundList
	roundList.append(random.randint(0,3))
	sleep(0.3)
	showList()

def showList():
	global roundList
	for i in roundList:
		ledAndSound(i)
		sleep(0.2)
	print("Your move!")

#
startNewGame()

sensorLastValues = [gyroSensor.get_gyro_data()['y'], mcp.read_adc(0),mcp.read_adc(1),mcp.read_adc(2)]
#potentiometer , fire, distance , gyro
#Main Loop
def updateSensorArray():
	global sensorLastValues
	sensorLastValues[0] = gyroSensor.get_gyro_data()['y']
	sensorLastValues[1] = mcp.read_adc(0)
	sensorLastValues[2] = mcp.read_adc(1)
	sensorLastValues[3] = mcp.read_adc(2)

while True:
	potentiometerValue = mcp.read_adc(0)
	fireSensorValue = mcp.read_adc(1)
	sleep(0.5) 
	distanceSensor = mcp.read_adc(2)
	accel_data = gyroSensor.get_accel_data()
	gyro_data = gyroSensor.get_gyro_data()
	if(abs(gyro_data['y'] - sensorLastValues[0]) > 60):
		print("gyro y change")
		print("last: ",sensorLastValues[0])
		print("current", gyro_data['y'])
		updateSensorArray()
		ledAndSound(0)
		sleep(1)
		checkUserInput(0)
	elif(abs(potentiometerValue - sensorLastValues[1]) > 300):
		print("potentiometer changed")
		print("last: ",sensorLastValues[1])
		print("current: ", potentiometerValue)
		updateSensorArray()
		ledAndSound(1)
		sleep(1)
		checkUserInput(1)
	elif(fireSensorValue < 75):
		print("fire changed")
		print("last: ",sensorLastValues[2])
		print("current: ", fireSensorValue)
		updateSensorArray()
		ledAndSound(2)
		sleep(1)
		checkUserInput(2)
	elif(abs(distanceSensor - sensorLastValues[3]) > 300):
		print("distaance changed")
		print("last: ",sensorLastValues[3])
		print("current: ", distanceSensor)
		updateSensorArray()
		ledAndSound(3)
		sleep(1)
		checkUserInput(3)
	time.sleep(0.1)

GPIO.cleanup()