import copy
from frinx_conductor_workers.frinx_rest import conductor_headers
import json

import requests

# Templates
create_schedule_tmpl = {
	"name": None,
	"workflowName": None,
	"workflowVersion": None,
	"cronString": None,
 	"enabled": None,
	"parallelRuns": False,
	"workflowContext": None,
    "correlationId": 'network-admin',
    "taskToDomain": None
}

SCHELLAR_URL = 'http://workflow-proxy:8088/schedule/'


def create_schedule(task):
    body = copy.deepcopy(create_schedule_tmpl)
    
    body['name'] = task['inputData']['workflow_name'] + ":" + task['inputData']['workflow_version']
    body['workflowName'] = task['inputData']['workflow_name'] 
    body['workflowVersion'] = str(task['inputData']['workflow_version'])
    body['cronString'] = str(task['inputData']['cron'])
    body['enabled'] = bool(task['inputData']['enabled'])
    
    if task['inputData']['workflow_context'] is not None:
        body['workflowContext'] = task['inputData']['workflow_context']

    response = requests.put(SCHELLAR_URL + body['name'], data=json.dumps(body), headers=conductor_headers)
    status = 'FAILED'
    if response.ok:
        status = 'COMPLETED'
        
    return {'status': status, 'output': {'url': SCHELLAR_URL, 'response_code': response.status_code, 'response_body': {}}, 'logs': []}



def start(cc):
    print('Starting Inventory workers')

    cc.register('SCHELLAR_create_schedule', {
        "description": '{"description": "create simple schedule", "labels": ["BASICS","MAIN","SCHELLAR"]}',
        "responseTimeoutSeconds": 60,
        "timeoutSeconds": 60,
        "inputKeys": [
            "workflow_name",
            "workflow_version",
            "enabled",
            "cron",
            "workflow_context"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, create_schedule)
