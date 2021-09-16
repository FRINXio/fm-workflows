from frinx_conductor_workers.frinx_rest import parse_response
from jinja2 import Template
from python_graphql_client import GraphqlClient
import json, copy

# graphql client settings
inventory_url = "http://inventory:8000/graphql"
inventory_headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Connection": "keep-alive",
    "x-tenant-id": "frinx",
    "DNT": "1"
}

client = GraphqlClient(endpoint=inventory_url, headers=inventory_headers)


def execute(body, variables):
    return client.execute(query=body, variables=variables)


# Templates

claim_resource_template = Template(
    """
    mutation ClaimResource($pool_id: ID!, $description: String!, $user_input: Map!{{ alternative_id_variable }}) {
    {{ claim_resource }}(
        poolId: $pool_id,
        description: $description,
        userInput: $user_input{{ alternative_id }})
    {
        id
        Properties
    }
    }"""
)

add_device_template = """ 
mutation  AddDevice($input: AddDeviceInput!) {
    addDevice(input: $input) {
        device {
            id
            name
            isInstalled
        }
    }
} """

install_device_template = """
mutation InstallDevice($id: String!){
  installDevice(id:$id){
    device{
      id
      name
    }
  }
} """

uninstall_device_template = """
mutation UninstallDevice($id: String!){
  uninstallDevice(id:$id){
    device{
      id
      name
    }
  }
} """

create_label_template = """ 
mutation CreateLabel($input: CreateLabelInput!) {
  createLabel(input: $input){
    label {
      name
      id
    }
  }
} """

cli_device_template = {
    "cli": {
        "cli-topology:host": "",
        "cli-topology:port": "",
        "cli-topology:transport-type": "ssh",
        "cli-topology:device-type": "",
        "cli-topology:device-version": "",
        "cli-topology:password": "",
        "cli-topology:username": "",
        "cli-topology:journal-size": "",
        "cli-topology:parsing-engine": ""
    }
}

netconf_device_template = {
    "netconf": {
        "netconf-node-topology:host": "",
        "netconf-node-topology:port": "",
        "netconf-node-topology:keepalive-delay": "",
        "netconf-node-topology:tcp-only": "",
        "netconf-node-topology:username": "",
        "netconf-node-topology:password": "",
        "uniconfig-config:uniconfig-native-enabled": "",
        "uniconfig-config:blacklist": {
            "uniconfig-config:path": []
        }
    }
}

task_body_template = {
    "name": "sub_task",
    "taskReferenceName": "",
    "type": "SUB_WORKFLOW",
    "subWorkflowParam": {
        "name": "",
        "version": 1
    }
}


def execute_inventory(body, variables):
    return client.execute(query=body, variables=variables)


def get_zone_id(zone_name):
    zone_id_device = "query { zones { edges { node {  id name } } } }"

    body = execute_inventory(zone_id_device, '')
    for node in body['data']['zones']['edges']:
        if node['node']['name'] == zone_name:
            return node['node']['id']


def get_device_info(device_name):
    devices = "query { devices { edges { node {  id name isInstalled } } } }"
    body = execute_inventory(devices, '')

    # if error
    for i in body:
        if i == "errors":
            return device_name, None, body['errors'][0]['message']

    # if device was found
    for node in body['data']['devices']['edges']:
        if node['node']['name'] == device_name:
            return node['node']['name'], node['node']['id'], node['node']['isInstalled']

    # if device was not found
    return device_name, None, None


def get_all_devices_info():
    devices = "query { devices { edges { node {  id name isInstalled } } } }"
    body = execute_inventory(devices, '')

    # if error
    for i in body:
        if i == "errors":
            return body['errors'][0]['message'], 404

    return body['data']['devices']['edges'], 200


def get_label_id(label_name):
    zone_id_device = "query { labels { edges { node {  id name } } } }"

    label_id = ''
    body = execute_inventory(zone_id_device, '')
    for node in body['data']['labels']['edges']:
        if node['node']['name'] == label_name:
            label_id = node['node']['id']

    if label_id == '':
        variables = {'input': {
            "name": label_name
        }}
        response = execute_inventory(create_label_template, variables)
        if response['data']['createLabel']['label']['name'] == label_name:
            label_id = response['data']['createLabel']['label']['id']
            return label_id
    else:
        return label_id


####################################################################################

def install_uninstall_device(task):
    if str(task['taskType']).find('_by_name') != -1:
        device_name, device_id, device_is_installed = get_device_info(task['inputData']['device_id'])

        if device_id is None:
            body = {"message": device_is_installed}
            return {'status': 'FAILED', 'output': {'url': inventory_url, 'response_code': 404, 'response_body': body},
                    'logs': []}

        variables = {
            "id": str(device_id)
        }
    else:
        variables = {
            "id": str(task['inputData']['device_id'])
        }

    if str(task['taskType']).find('uninstall') == -1:
        # install task
        response = execute_inventory(install_device_template, variables)
        task_type = "installDevice"
    else:
        # uninstall task
        response = execute_inventory(uninstall_device_template, variables)
        task_type = "uninstallDevice"

    for i in response:
        if i == "errors":
            body = {"message": response['errors'][0]['message']}
            return {'status': 'FAILED', 'output': {'url': inventory_url, 'response_code': 404, 'response_body': body},
                    'logs': []}

    body = {
        "id": response['data'][task_type]['device']['id'],
        "name": response['data'][task_type]['device']['name']
    }

    return {'status': 'COMPLETED', 'output': {'url': inventory_url, 'response_code': 200, 'response_body': body},
            'logs': []}


def installed_device_dynamic_fork_tasks(task):

    task = task['inputData']['task']

    response, code = get_all_devices_info()

    if code == 200:
        dynamic_tasks = []
        for device_id in response:
            task_body = copy.deepcopy(task_body_template)
            task_body["taskReferenceName"] = device_id['node']['name']
            task_body["subWorkflowParam"]["name"] = task
            # if optional == "true":
            #     task_body['optional'] = "True"

            dynamic_tasks.append(task_body)

        dynamic_tasks_i = {}
        for device_id in response:
            per_device_params = dict({})
            per_device_params.update({"device_id": device_id['node']['name']})
            dynamic_tasks_i.update({device_id['node']['name']: per_device_params})

        return {'status': 'COMPLETED', 'output': {'url': inventory_url,
                                                  'dynamic_tasks_i': dynamic_tasks_i,
                                                  'dynamic_tasks': dynamic_tasks},
                'logs': []}
    else:
        return {'status': 'FAILED', 'output': {'url': inventory_url, 'response_code': code, 'response_body': response},
                'logs': []}


def installed_device(task):
    device_name, device_id, device_is_installed = get_device_info(task['inputData']['device_id'])

    if device_id is not None:
        data = {
            "name": device_name,
            "id": device_id,
            "isInstalled": device_is_installed
        }
        return {'status': 'COMPLETED', 'output': {'url': inventory_url, 'response_code': 200, 'response_body': data},
                'logs': []}
    else:
        data = {"message": device_is_installed}
        return {'status': 'FAILED', 'output': {'url': inventory_url, 'response_code': 404, 'response_body': data},
                'logs': []}


def add_cli_device(task):
    body = copy.deepcopy(cli_device_template)

    body["cli"]["cli-topology:host"] = task['inputData']['host']
    body["cli"]["cli-topology:port"] = task['inputData']['port']
    body["cli"]["cli-topology:transport-type"] = task['inputData']['protocol']
    body["cli"]["cli-topology:device-type"] = task['inputData']['type']
    body["cli"]["cli-topology:device-version"] = task['inputData']['version']
    body["cli"]["cli-topology:username"] = task['inputData']['username']
    body["cli"]["cli-topology:password"] = task['inputData']['password']
    body["cli"]["cli-topology:journal-size"] = task['inputData']['journal-size']
    body["cli"]["cli-topology:parsing-engine"] = task['inputData']['parsing-engine']

    variables = {'input': {
        "name": task['inputData']['device_id'],
        "zoneId": get_zone_id(task['inputData']['uniconfig_zone']),
        "serviceState": task['inputData']["service_state"],
        "mountParameters": str(body).replace("'", '"'),
    }}

    response = execute_inventory(add_device_template, variables)

    for i in response:
        if i == "errors":
            body = {"message": response['errors'][0]['message']}
            return {'status': 'FAILED', 'output': {'url': inventory_url,
                                                   'response_code': 404,
                                                   'response_body': body},
                    'logs': []}

    body = {
        "id": response['data']['addDevice']['device']['id'],
        "name": response['data']['addDevice']['device']['name'],
        "isInstalled": response['data']['addDevice']['device']['isInstalled']
    }

    return {'status': 'COMPLETED', 'output': {'url': inventory_url, 'response_code': 200, 'response_body': body},
            'logs': []}


def add_netconf_device(task):
    body = copy.deepcopy(netconf_device_template)

    body["netconf"]["netconf-node-topology:host"] = task['inputData']['host']
    body["netconf"]["netconf-node-topology:port"] = task['inputData']['port']
    body["netconf"]["netconf-node-topology:username"] = task['inputData']['username']
    body["netconf"]["netconf-node-topology:password"] = task['inputData']['password']
    body["netconf"]["netconf-node-topology:keepalive-delay"] = task['inputData']['keepalive-delay']
    body["netconf"]["netconf-node-topology:tcp-only"] = task['inputData']['tcp-only']
    body["netconf"]["uniconfig-config:uniconfig-native-enabled"] = task['inputData']['uniconfig-native']

    if "blacklist" in task["inputData"] and task["inputData"]["blacklist"] is not None:
        model_array = [model.strip() for model in task["inputData"]["blacklist"].split(",")]
        for model in model_array:
            body["netconf"]["uniconfig-config:blacklist"]["uniconfig-config:path"].append(model)

    variables = {'input': {
        "name": task['inputData']['device_id'],
        "zoneId": get_zone_id(task['inputData']['uniconfig_zone']),
        "serviceState": task['inputData']["service_state"],
        "mountParameters": str(body).replace("'", '"'),
    }}

    if task["inputData"]['labels'] is not None:
        label_id = get_label_id(task["inputData"]['labels'])
        variables['input']['labelIds'] = label_id

    response = execute_inventory(add_device_template, variables)

    for i in response:
        if i == "errors":
            body = {"message": response['errors'][0]['message']}
            return {'status': 'FAILED', 'output': {'url': inventory_url,
                                                   'response_code': 404,
                                                   'response_body': body},
                    'logs': []}

    body = {
        "id": response['data']['addDevice']['device']['id'],
        "name": response['data']['addDevice']['device']['name'],
        "isInstalled": response['data']['addDevice']['device']['isInstalled']
    }

    return {'status': 'COMPLETED', 'output': {'url': inventory_url, 'response_code': 200, 'response_body': body},
            'logs': []}


def start(cc):
    print('Starting Inventory workers')

    cc.register('INVENTORY_install_device_by_name', {
        "description": '{"description": "Install device by name", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 60,
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_uninstall_device_by_name', {
        "description": '{"description": "Install device by name", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_install_device_by_id', {
        "description": '{"description": "Install device by ID number", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 60,
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_uninstall_device_by_id', {
        "description": '{"description": "Install device by ID number", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_get_device_info', {
        "description": '{"description": "Get device inventory ID, Name and installed status", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 10,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, installed_device)

    cc.register('INVENTORY_get_all_devices_as_dynamic_fork_tasks', {
        "name": "INVENTORY_get_all_devices_as_dynamic_fork_tasks",
        "description": '{"description": "get all devices as dynamic fork tasks", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "task"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    }, installed_device_dynamic_fork_tasks)

    cc.register('INVENTORY_add_cli_device', {
        "description": '{"description": "add a CLI device to inventory database", "labels": ["BASICS","MAIN","INVENTORY","CLI"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "type",
            "version",
            "host",
            "protocol",
            "port",
            "username",
            "password",
            "journal-size",
            "parsing-engine",
            "labels",
            "uniconfig_zone",
            "service_state"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, add_cli_device)

    cc.register('INVENTORY_add_netconf_device', {
        "description": '{"description": "add a Netconf device to inventory database", "labels": ["BASICS","MAIN","INVENTORY","NETCONF"]}',
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "device_id",
            "host",
            "port",
            "keepalive-delay",
            "tcp-only",
            "username",
            "password",
            "uniconfig-native",
            "blacklist",
            "labels",
            "uniconfig_zone",
            "service_state"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, add_netconf_device)
