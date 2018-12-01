import RPi.GPIO as GPIO
import time
import wiringpi
from time import sleep
import random

#Set up script to use the right pin configuration
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

gpioSound = 5
Led_Array = [4,17,27,22]
Button_Array = [18,23,24,25]
mapping = {0:(4,440), 1:(17,523),2:(27,659),3:(22,784)}

wiringpi.wiringPiSetupGpio()
wiringpi.softToneCreate(gpioSound)

roundList = []
roundListIterator = 0

#Set all the buttons pins to inputs
for index in range(len(Button_Array)):
    GPIO.setup(Button_Array[index], GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

#Set all the Led pins to outputs
for index in range(len(Led_Array)):
    GPIO.setup(Led_Array[index], GPIO.OUT)

#------------ button Callback
def button0_callBack(channel):
        print("Pushed 0")
        ledAndSound(0)
        sleep(1)
        checkUserInput(0)

def button1_callBack(channel):
        print("Pushed 1")
        ledAndSound(1)
        sleep(1)
        checkUserInput(1)

def button2_callBack(channel):
        print("Pushed 2")
        ledAndSound(2)
        sleep(1)
        checkUserInput(2)

def button3_callBack(channel):
        print("Pushed 3")
        ledAndSound(3)
        sleep(1)
        checkUserInput(3)


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
        #startShow = [0,1,2,3,3,2,1,0]
        startShow = [0,1,1,0]
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


GPIO.add_event_detect(Button_Array[0],GPIO.RISING,callback=button0_callBack)
GPIO.add_event_detect(Button_Array[1],GPIO.RISING,callback=button1_callBack)
GPIO.add_event_detect(Button_Array[2],GPIO.RISING,callback=button2_callBack)
GPIO.add_event_detect(Button_Array[3],GPIO.RISING,callback=button3_callBack)

startNewGame()
message = input("Press enter to quit \n\n")

GPIO.cleanup()
