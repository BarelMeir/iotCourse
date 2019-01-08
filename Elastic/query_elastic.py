from elasticsearch import Elasticsearch, RequestsHttpConnection
import boto3
from requests_aws4auth import AWS4Auth
import json
region = 'eu-west-1'
session = boto3.session.Session(region_name=region)
credentials = session.get_credentials()

host = 'search-idc-7dyp7fwnklhj22hwzpuoa5hgsy.eu-west-1.es.amazonaws.com'
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key, region, 'es')

es = Elasticsearch(
    hosts=[{'host': host, 'port': 443}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)
query = {
    "query": {
        "range": {
            "time": {
                "gte": "now-5s/s"
            }
        }
    }
}
result = es.search(index='meir_miran_data', body=query)
print(json.dumps(result))
