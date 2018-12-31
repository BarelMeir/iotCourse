from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import argparse
import json
from sense_hat import SenseHat
import RPi.GPIO as GPIO
import wiringpi
from time import sleep
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


# Change according to your configuration
host = 'a1rpddawph4ysg-ats.iot.eu-west-1.amazonaws.com'
rootCA = './root-CA.crt'
privateKey = './56075c5af2-private.pem.key'
cert = './56075c5af2-certificate.pem.crt'
deviceId = 'Meir-Miran'
thingName = deviceId
telemetry = None
topic = thingName + '/Potentiometer'
interval = 1

# Custom MQTT message callback
def customCallback(client, userdata, message):
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")

# Custom Shadow callbacks
def customShadowCallback_Update(payload, responseStatus, token):
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    if responseStatus == "timeout":
        print("Update request " + token + " time out!")
    if responseStatus == "accepted":
        payloadDict = json.loads(payload)
        print("~~~~~~~~~~~~~~~~~~~~~~~")
        print("Update request with token: " + token + " accepted!")
        print("property: " + str(payloadDict["state"]))
        print("~~~~~~~~~~~~~~~~~~~~~~~\n\n")
    if responseStatus == "rejected":
        print("Update request " + token + " rejected!")


def customShadowCallback_Get(payload, responseStatus, token):
    global interval
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print ("customShadowCallback_GETTTT")
    payloadDict = json.loads(payload)
    if 'interval' in payloadDict['state']:
        interval = payloadDict['state']['interval']

    if 'delta' in payloadDict['state']:
        newPayload = {
        "state": payloadDict['state']['delta']
        }
        customShadowCallback_Delta(newPayload, None, None)
        return
    print("++++++++GET++++++++++")
    reportedPotential = str(payloadDict['state']['reported']['Potentiometer']).lower()
    print("reported potential: " + reportedPotential)
    # print("version: " + str(payloadDict["version"]))
    print("+++++++++++++++++++++++\n\n")
    

def customShadowCallback_Delta(payload, responseStatus, token):
    global interval
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    print ("HELLO WORLD!!!")
    payloadDict = json.loads(payload)
    # print(str(payloadDict))
    if 'interval' in payloadDict['state']:
        interval = payloadDict['state']['interval']
    reportedColor = str(payloadDict['state']['Potentiometer']).lower()
    newPayload = '{"state":{"reported":' + json.dumps(payloadDict['state']) + '}}'
    deviceShadowHandler.shadowUpdate(newPayload, customShadowCallback_Update, 5)

# Configure logging
logger = logging.getLogger("AWSIoTPythonSDK.core")
logger.setLevel(logging.WARNING)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Init AWSIoTMQTTClient
myAWSIoTMQTTShadowClient = None
myAWSIoTMQTTShadowClient = AWSIoTMQTTShadowClient(deviceId)
myAWSIoTMQTTShadowClient.configureEndpoint(host, 8883)
myAWSIoTMQTTShadowClient.configureCredentials(rootCA, privateKey, cert)

# AWSIoTMQTTClient connection configuration
myAWSIoTMQTTShadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
myAWSIoTMQTTShadowClient.configureConnectDisconnectTimeout(10)  # 10 sec
myAWSIoTMQTTShadowClient.configureMQTTOperationTimeout(5)  # 5 sec

# Connect and subscribe to AWS IoT
myAWSIoTMQTTShadowClient.connect()

# Create a deviceShadow with persistent subscription
deviceShadowHandler = myAWSIoTMQTTShadowClient.createShadowHandlerWithName(
    thingName, True)
# Listen on deltas
deviceShadowHandler.shadowRegisterDeltaCallback(customShadowCallback_Delta)
deviceShadowHandler.shadowGet(customShadowCallback_Get,5)

myMQTTClient = myAWSIoTMQTTShadowClient.getMQTTConnection()
# Infinite offline Publish queueing
myMQTTClient.configureOfflinePublishQueueing(-1)
myMQTTClient.configureDrainingFrequency(2)  # Draining: 2 Hz
myMQTTClient.configureConnectDisconnectTimeout(10)  # 10 sec
myMQTTClient.configureMQTTOperationTimeout(5)  # 5 sec
# Loop forever and wait for joystic

while True:
	global interval
    potentiometerValue = mcp.read_adc(0)
    payload = {
        'Potentiometer': potentiometerValue,
        'interval' : interval
    }
    print("+++ potentiometer Data is +++")
    print (payload)
    print("+++ End of Data +++")

    print(topic)
    myMQTTClient.publish(topic,json.dumps(payload),1)
    time.sleep(interval)
