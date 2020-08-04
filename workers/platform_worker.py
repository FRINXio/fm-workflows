from __future__ import print_function

import requests
from frinx_rest import odl_url_base, odl_credentials, parse_response, add_uniconfig_tx_cookie

from string import Template

odl_url_components = odl_url_base + "/data/network-topology:network-topology/topology=unified/node=$id/yang-ext:mount/frinx-openconfig-platform:components?content=nonconfig"


def read_components(task):
    device_id = task['inputData']['device_id']
    uniconfig_tx_id = task['inputData']['uniconfig_tx_id'] if 'uniconfig_tx_id' in task["inputData"] else ""

    id_url = Template(odl_url_components).substitute({"id": device_id})

    r = requests.get(id_url, headers=add_uniconfig_tx_cookie(uniconfig_tx_id), auth=odl_credentials)
    response_code, response_json = parse_response(r)

    if response_code == requests.codes.ok:
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
    print('Starting Platform workers')

    cc.register('OC-PLATFORM_read_components', {
        "name": "OC-PLATFORM_read_components",
        "description": "{\"description\": \"Read components in openconfig format\", \"labels\": [\"DEMO\",\"PLATFORM\",\"UNIFIED\",\"OPENCONFIG\"]}",
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
    cc.start('OC-PLATFORM_read_components', read_components, False)
