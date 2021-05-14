from __future__ import print_function

import json
import copy

import requests
from string import Template

from frinx_conductor_workers.frinx_rest import elastic_url_base, uniconfig_url_base, additional_uniconfig_request_params, parse_response, elastic_headers, add_uniconfig_tx_cookie

build_lldp_url = uniconfig_url_base + "/operations/lldptopo:build"
export_lldp_url = uniconfig_url_base + "/operations/lldptopo:export"
read_lldp_url = uniconfig_url_base + "/data/network-topology:network-topology/topology=$topo?content=nonconfig"
inventory_lldp_url = elastic_url_base + "/inventory-lldp/lldp/$id"


lldp_build_template = {
  "input": {
    "node-aggregation": "",
    "link-aggregation": "",

    "per-node-read-timeout": 0,
    "concurrent-read-nodes": 0,

    "destination-topology": ""
  }
}


def build_lldp(task):
    topo_id = task['inputData']['destination-topology']

    lldp_body = copy.deepcopy(lldp_build_template)

    lldp_body["input"]["node-aggregation"] = task['inputData']['node-aggregation']
    lldp_body["input"]["link-aggregation"] = task['inputData']['link-aggregation']
    lldp_body["input"]["per-node-read-timeout"] = task['inputData']['per-node-read-timeout']
    lldp_body["input"]["concurrent-read-nodes"] = task['inputData']['concurrent-read-nodes']
    lldp_body["input"]["destination-topology"] = task['inputData']['destination-topology']

    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    r = requests.post(build_lldp_url, data=json.dumps(lldp_body), headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.created or response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': build_lldp_url,
                                                  'request_body': lldp_body,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["LLDP topology built and stored in %s" % topo_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': build_lldp_url,
                                               'request_body': lldp_body,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Failed to build LLDP topology %s" % topo_id]}


lldp_export_template = {
  "input": {
  }
}


def export_lldp(task):
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] \
        if 'inputData' in task and 'uniconfig_tx_id' in task['inputData'] else ""
    lldp_body = copy.deepcopy(lldp_export_template)

    r = requests.post(export_lldp_url, data=json.dumps(lldp_body), headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.created or response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': export_lldp_url,
                                                  'request_body': lldp_body,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["LLDP topology exported"]}
    else:
        return {'status': 'FAILED', 'output': {'url': export_lldp_url,
                                               'request_body': lldp_body,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Failed to export LLDP topology"]}


def read_lldp(task):
    topo_id = task['inputData']['destination-topology']

    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    id_url = Template(read_lldp_url).substitute({"topo": topo_id})

    r = requests.get(id_url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), **additional_uniconfig_request_params)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.created or response_code == requests.codes.ok:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': ["LLDP topology read: %s" % topo_id]}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': ["Failed to read LLDP topology: %s" % topo_id]}


def store_lldp(task):
    topo_id = task['inputData']['destination-topology']
    topo = task['inputData']['content']

    id_url = Template(inventory_lldp_url).substitute({"id": topo_id})

    add_body = {}
    add_body["lldp"] = task['inputData']['content']

    r = requests.post(id_url, data=json.dumps(add_body), headers=elastic_headers)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok or response_code == requests.codes.created:
        return {'status': 'COMPLETED', 'output': {'url': id_url,
                                                  'response_code': response_code,
                                                  'response_body': response_json},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': id_url,
                                               'response_code': response_code,
                                               'response_body': response_json},
                'logs': []}


def start(cc):
    print('Starting LLDP topology workers')

    cc.register('LLDP_build_topology', {
        "name": "LLDP_build_topology",
        "description": "{\"description\": \"Build lldp topology\", \"labels\": [\"DEMO\",\"LLDP\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "node_aggregation",
            "link_aggregation",
            "per-node-read-timeout",
            "concurrent-read_nodes",
            "destination-topology",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            'request_body'
            "response_code",
            "response_body"
        ]
    })
    cc.start('LLDP_build_topology', build_lldp, False)

    cc.register('LLDP_export_topology', {
        "name": "LLDP_export_topology",
        "description": "{\"description\": \"Export lldp topology\", \"labels\": [\"DEMO\",\"LLDP\"]}",
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
            'request_body'
            "response_code",
            "response_body"
        ]
    })
    cc.start('LLDP_export_topology', export_lldp, False)

    cc.register('LLDP_read_topology', {
        "name": "LLDP_read_topology",
        "description": "{\"description\": \"Read lldp topology\", \"labels\": [\"DEMO\",\"LLDP\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "destination-topology",
            "uniconfig_tx_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('LLDP_read_topology', read_lldp, False)

    cc.register('LLDP_store_topology', {
        "name": "LLDP_store_topology",
        "description": "{\"description\": \"Store lldp topology in database\", \"labels\": [\"DEMO\",\"LLDP\"]}",
        "retryCount": 0,
        "timeoutSeconds": 60,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "destination-topology",
            "content"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    })
    cc.start('LLDP_store_topology', store_lldp, False)
