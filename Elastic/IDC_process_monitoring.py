
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import logging
import time
import argparse
import json
#from sense_hat import SenseHat

# Change according to your configuration
host = 'a1rpddawph4ysg-ats.iot.eu-west-1.amazonaws.com'
rootCA = './root-CA.crt'
privateKey = './certificates/56075c5af2-private.pem.key'
cert = './certificates/56075c5af2-certificate.pem.crt'
thingName = 'Meir-Miran'
deviceId = thingName
telemetry = None
topic = thingName + '/raspi/data'
interval = 1

# SendHat configuration
#sense = SenseHat()
color = {}
color['yellow'] = (255, 255, 0)
color['red'] = (255, 0, 0)
color['green'] = (0, 255, 0)

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
    payloadDict = json.loads(payload)
    if 'delta' in payloadDict['state']:
        newpayload = {
            'state': payloadDict['state']['delta']
        }
        customShadowCallback_Delta(json.dumps(newpayload), None, None)
        return
    print("++++++++GET++++++++++")
    if 'interval' in payloadDict['state']['desired']:
        interval = int(payloadDict['state']['desired']['interval'])
    if 'color' in payloadDict['state']['desired']:
        reportedColor = str(payloadDict['state']['desired']['color']).lower()
        print("reported color: " + reportedColor)
        print("+++++++++++++++++++++++\n\n")
        # if reportedColor in ['red', 'green', 'yellow']:
        #     sense.clear(color[reportedColor])
        # else:
        #     sense.clear()
    

def customShadowCallback_Delta(payload, responseStatus, token):
    global interval
    # payload is a JSON string ready to be parsed using json.loads(...)
    # in both Py2.x and Py3.x
    payloadDict = json.loads(payload)
    print("++++++++DELTA++++++++++")
    print(payloadDict)
    print("++++++++DELTA++++++++++")
    if 'interval' in payloadDict['state']:
        interval = int(payloadDict['state']['interval'])
    if 'color' in payloadDict['state']:
        reportedColor = str(payloadDict['state']['color']).lower()
        print("reported color: " + reportedColor)
        print("+++++++++++++++++++++++\n\n")
        # if reportedColor in ['red', 'green', 'yellow']:
        #     sense.clear(color[reportedColor])
        # else:
        #     sense.clear()
    newPayload = '{"state":{"reported":' + json.dumps(payloadDict['state']) + '}}'
    print("++++++++NEW_REPORTED++++++++++")
    print(newPayload)
    print("++++++++NEW_REPORTED++++++++++")
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
# Use the sensehat module

time.sleep(2)
import psutil
while True:
    plist = []
    for process in psutil.process_iter():
        plist.append(
            {'name': process.name(), 'create time': process.create_time()})
    payload = {
        'CPU Utilization': psutil.cpu_percent(),
        'num CPUs': psutil.cpu_count(),
        'virtual Memory utilization': psutil.virtual_memory()[2],
        'disk used': psutil.disk_usage('/')[3],
        'process list': plist
    }
    print(topic)
    print(json.dumps(payload))
    myMQTTClient.publish(topic,json.dumps(payload),1)
    time.sleep(interval)
