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
	#startShow = [0,1,1,0]
	for i in startShow:
		ledAndSound(i)
		sleep(0.2)
	print("start!")
	sleep(1.5)
	addToList()

def endRound():
	print("End round")
	#endShow = [0,0,1,1,2,2,3,3]
	endShow = [1,1,2,2]
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

#Main Loop
while True:
	potentiometerValue = mcp.read_adc(0)
	fireSensorValue = mcp.read_adc(1) 
	distanceSensor = mcp.read_adc(2)
	accel_data = gyroSensor.get_accel_data()
	gyro_data = gyroSensor.get_gyro_data()
	if(distanceSensor < 100):
		print("distance < 100")
		ledAndSound(0)
		sleep(1)
		checkUserInput(0)

	#elif(potentiometerValue )




	# # Read all the ADC channel values in a list.
 #    values = [0]*8
 #    for i in range(8):
 #        # The read_adc function will get the value of the specified channel (0-7).
 #        values[i] = mcp.read_adc(i)
 #    # Print the ADC values.
 #    #print('| {0:>4} | {1:>4} | {2:>4}'.format(*values))

	
	#print ("accel_Data ", accel_data)
	#print ("gyro_data", gyro_data)

	# print("%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f\t%1.2f" % (accel_data['x'], accel_data['x'], accel_data['y'], gyro_data['x'], gyro_data['y'], gyro_data['z']))


	# sleeps for one second
	time.sleep(0.1)

GPIO.cleanup()
