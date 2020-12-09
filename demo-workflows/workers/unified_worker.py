from __future__ import print_function

import requests
import json
import copy
from string import Template
from frinx_rest import uniconfig_url_base, additional_uniconfig_request_params, parse_response, add_uniconfig_tx_cookie
import uniconfig_worker

uniconfig_url_unified_oper_shallow = uniconfig_url_base + "/data/network-topology:network-topology/topology=unified?content=nonconfig&depth=3"
uniconfig_url_unified_oper = uniconfig_url_base + "/data/network-topology:network-topology/topology=unified?content=nonconfig"
uniconfig_url_unified_oper_mount = uniconfig_url_base + "/data/network-topology:network-topology/topology=unified/node=$id?content=nonconfig"
uniconfig_url_unified_mount = uniconfig_url_base + "/data/network-topology:network-topology/topology=unified/node=$id"


def execute_read_unified_topology_operational(task):
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] \
        if 'inputData' in task and 'uniconfig_tx_id' in task['inputData'] else ""
    response_code, response_json = read_all_devices(uniconfig_url_unified_oper, uniconfig_tx_id)

    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': uniconfig_url_unified_oper,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': uniconfig_url_unified_oper,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': []}


def read_all_devices(url, uniconfig_tx_id):
    r = requests.get(url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    actual_nodes = response_json['topology'][0]['node']
    filtered_nodes = []

    for node in actual_nodes:
        if node['unified-topology:connection-status'] == "installed":
            filtered_nodes.append(node)

    response_json['topology'][0].pop('node')
    response_json['topology'][0].update({'node': filtered_nodes})

    return response_code, response_json


task_body_template = {
    "name": "sub_task",
    "taskReferenceName": "",
    "type": "SUB_WORKFLOW",
    "subWorkflowParam": {
        "name": "",
        "version": 1
    }
}


def get_all_devices_as_dynamic_fork_tasks(task):
    subworkflow = task['inputData']['task']
    add_params = task['inputData']['task_params']
    optional = task['inputData']['optional'] if 'optional' in task['inputData'] else "false"
    add_params = json.loads(add_params) if isinstance(add_params, str) and add_params is not '' else (add_params if add_params else {})
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    response_code, response_json = read_all_devices(uniconfig_url_unified_oper_shallow, uniconfig_tx_id)

    if response_code == requests.codes.ok:
        ids = [nodes["node-id"] for nodes in response_json["topology"][0]["node"]]

        dynamic_tasks_i = {}
        for device_id in ids:
            per_device_params = dict(add_params)
            per_device_params.update({"device_id": device_id})
            dynamic_tasks_i.update({device_id: per_device_params})

        dynamic_tasks = []
        for device_id in ids:
            task_body = copy.deepcopy(task_body_template)
            if optional == "true":
                task_body['optional'] = True
            task_body["taskReferenceName"] = device_id
            task_body["subWorkflowParam"]["name"] = subworkflow
            dynamic_tasks.append(task_body)

        return {'status': 'COMPLETED', 'output': {'url': uniconfig_url_unified_oper_shallow,
                                                  'dynamic_tasks_i': dynamic_tasks_i,
                                                  'dynamic_tasks': dynamic_tasks},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': uniconfig_url_unified_oper_shallow,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': []}


def read_structured_data(task):
    device_id = task['inputData']['device_id']
    uri = task['inputData']['uri']
    uri = uniconfig_worker.apply_functions(uri)
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    id_url = Template(uniconfig_url_unified_mount).substitute({"id": device_id}) + "/yang-ext:mount" + (uri if uri else "") + "?content=config"

    r = requests.get(id_url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s read successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to read device with ID %s" % device_id]}


def write_structured_data(task):
    device_id = task['inputData']['device_id']
    uri = task['inputData']['uri']
    uri = uniconfig_worker.apply_functions(uri)
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    template = task['inputData']['template']
    params = task['inputData']['params'] if task['inputData']['params'] else {}

    data_json = template if isinstance(template, str) else json.dumps(template if template else {})
    data_json = Template(data_json).substitute(params)

    id_url = Template(uniconfig_url_unified_mount).substitute({"id": device_id}) + "/yang-ext:mount" + (uri if uri else "")
    id_url = Template(id_url).substitute(params)

    r = requests.put(id_url, data=data_json, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.no_content or response_code == requests.codes.created:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'request_url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s updated successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'request_url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to update device with ID %s" % device_id]}


def delete_structured_data(task):
    device_id = task['inputData']['device_id']
    uri = task['inputData']['uri']
    uri = uniconfig_worker.apply_functions(uri)
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    id_url = Template(uniconfig_url_unified_mount).substitute({"id": device_id}) + "/yang-ext:mount" + (uri if uri else "")

    r = requests.delete(id_url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.no_content:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'request_url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Mountpoint with ID %s updated successfully" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'request_url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unable to update device with ID %s" % device_id]}


def execute_check_unified_node_exists(task):
    device_id = task['inputData']['device_id']
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    id_url = Template(uniconfig_url_unified_oper_mount).substitute({"id": device_id})

    r = requests.get(id_url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code != requests.codes.not_found:
        # Mountpoint with such ID already exists
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["Unified mountpoint with ID %s exists" % device_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Unified mountpoint with ID %s doesn't exist" % device_id]}


def start(cc):
    print('Starting Unified workers')

    cc.register('UNIFIED_read_unified_topology_operational', {
        "name": "UNIFIED_read_unified_topology_operational",
        "description": "{\"description\": \"Read operational state of Unified\", \"labels\": [\"BASICS\",\"UNIFIED\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('UNIFIED_read_unified_topology_operational', execute_read_unified_topology_operational, False)

    cc.register('UNIFIED_get_all_devices_as_dynamic_fork_tasks', {
        "name": "UNIFIED_get_all_devices_as_dynamic_fork_tasks",
        "description": "{\"description\": \"get all devices in unified topology as workflow tasks\", \"labels\": [\"BASICS\",\"UNIFIED\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "task",
            "task_params",
            "optional",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    })
    cc.start('UNIFIED_get_all_devices_as_dynamic_fork_tasks', get_all_devices_as_dynamic_fork_tasks, False)

    cc.register('UNIFIED_read_structured_device_data', {
        "name": "UNIFIED_read_structured_device_data",
        "description": "{\"description\": \"Read device configuration or operational data in structured format e.g. openconfig\", \"labels\": [\"BASICS\",\"UNIFIED\",\"OPENCONFIG\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "uri",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('UNIFIED_read_structured_device_data', read_structured_data, False)

    cc.register('UNIFIED_write_structured_device_data', {
        "name": "UNIFIED_write_structured_device_data",
        "description": "{\"description\": \"Write device configuration data in structured format e.g. openconfig\", \"labels\": [\"BASICS\",\"UNIFIED\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "uri",
            "template",
            "params",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "request_url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('UNIFIED_write_structured_device_data', write_structured_data, False)

    cc.register('UNIFIED_delete_structured_device_data', {
        "name": "UNIFIED_delete_structured_device_data",
        "description": "{\"description\": \"Delete device configuration data in structured format e.g. openconfig\", \"labels\": [\"BASICS\",\"UNIFIED\",\"OPENCONFIG\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "uri",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "request_url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('UNIFIED_delete_structured_device_data', delete_structured_data, False)

    cc.register('UNIFIED_check_unified_node_exists', {
        "name": "UNIFIED_check_unified_node_exists",
        "description": "{\"description\": \"check unified node exists\", \"labels\": [\"BASICS\",\"UNIFIED\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('UNIFIED_check_unified_node_exists', execute_check_unified_node_exists, False)
