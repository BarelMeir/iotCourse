import boto3
import json

client = boto3.client('iot-data')

response = client.update_thing_shadow(
	thingName = 'Meir-Miran'
	payload= json.dumps({"state": {"desired":{interval : 3}}})
)

print (response)
