from datetime import datetime
import os

from influxdb_client import InfluxDBClient, BucketsApi
from influxdb_client.client.write_api import SYNCHRONOUS
from frinx_conductor_workers.frinx_rest import influxdb_url_base

# You can generate an API token from the "API Tokens Tab" in the UI
token = os.getenv("DOCKER_INFLUXDB_INIT_ADMIN_TOKEN","eyJrIjoiN09MSVpVZjlVRG1xNHlLNXpVbmZJOXFLWU1GOXFxNEIiLCJuIjoic3Nzc3MiLCJpZCI6MX0")
org = os.getenv("DOCKER_INFLUXDB_INIT_ORG","frinx-machine")

def create_bucket_if_not_exist(task):
    try: 

        bucket_name = task['inputData']['bucket']

        if bucket_name is '':
            return {'status': 'FAILED', 'output': {'url': influxdb_url_base, 'response_code': 500, 'response_body': "Failed"}, 'logs': []}

        with InfluxDBClient(url=influxdb_url_base, token=token, org=org) as client:

            bucket_api=client.buckets_api()
            bucket = bucket_api.find_bucket_by_name(bucket_name)
            if bucket != None:
                print(bucket.name)
                return {'status': 'COMPLETED', 'output': {'url': influxdb_url_base, 'response_code': 200, 'bucket_name': bucket.name, 'response_body': "Bucket with name " + bucket.name + " exist before"}, 'logs': []}
            else:
                bucket = bucket_api.create_bucket(bucket_name=bucket_name, org=org)
                print(bucket.name)
                return {'status': 'COMPLETED', 'output': {'url': influxdb_url_base, 'response_code': 200, 'bucket_name': bucket.name, 'response_body': "Created new bucket with name " + bucket.name}, 'logs': []}
    except:
        return {'status': 'FAILED', 'output': {'url': "influxdb", 'response_code': 500, 'response_body': "Creating of bucket was unsucessful"},
                    'logs': []}


def store_ops_data(task):
    try:
        measurement = task['inputData']['measurement']
        tags = task['inputData']['tags']
        fields = task['inputData']['fields']
        bucket = task['inputData']['bucket']

        with InfluxDBClient(url=influxdb_url_base, token=token, org=org) as client:

            write_api = client.write_api(write_options=SYNCHRONOUS)

            dict_structure = {
                "measurement": measurement,
                "tags": tags,
                "fields": fields,
                "time": datetime.utcnow()
            }

            write_api.write(bucket, org, dict_structure)
            client.close()

        return {'status': 'COMPLETED', 'output': {'url': "influxdb", 'response_code': 200, 'response_body': "Write to influx db was successful"},
                    'logs': []}
    except:
        return {'status': 'FAILED', 'output': {'url': "influxdb", 'response_code': 500, 'response_body': "Write to influx db was unsuccessful"},
                    'logs': []}





def start(cc):
    print('Starting InfluxDB workers')

    cc.register('INFLUXDB_create_bucket_if_not_exist', {
        "description": '{"description": "create bucket in InfluxDB db if not exist", "labels": ["INFLUXDB"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "bucket"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "bucket_name",
            "response_body"
        ]
    }, create_bucket_if_not_exist)

    cc.register('INFLUXDB_write_data', {
        "description": '{"description": "write data to InfluxDB", "labels": ["INFLUXDB"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "measurement",
            "tags",
            "fields",
            "bucket"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, store_ops_data)

