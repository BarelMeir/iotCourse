import boto3

client = boto3.client('iot-data')

response = client.update_thing_shadow(
	thingName = 'Meir-Miran-Raspi'
	payload= json.dumps({"desired":{interval : 3}})
)

print (response)
