from python_graphql_client import GraphqlClient
import copy
import math
import json
from frinx_conductor_workers.frinx_rest import x_tenant_id, inventory_url_base

# graphql client settings
inventory_headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Connection": "keep-alive",
    "x-tenant-id": x_tenant_id,
    "DNT": "1",
    "Keep-Alive": "timeout=5"
}

client = GraphqlClient(endpoint=inventory_url_base, headers=inventory_headers)


def execute(body, variables):
    return client.execute(query=body, variables=variables)


# Templates
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

device_page_template = """
query GetDevices(
  $first: Int!, 
  $after: String!,
  $labels: [String!]
) {
  devices(first: $first, after: $after, filter: { labels: $labels } ) {
    pageInfo {
      startCursor
      endCursor
      hasPreviousPage
      hasNextPage
    }
  }
} """

device_page_id_template = """
query GetDevices($labels: [String!], $first: Int!, $after: String!) {
  devices( filter: { labels: $labels}, first:$first, after:$after) {
    pageInfo {
      startCursor
      endCursor
      hasPreviousPage
      hasNextPage
    }
    edges {
      node {
        name
        id
      }
    }
  }
} """

device_info_template = """
query Devices(
  $labels: [String!]
  $deviceName: String
) {
  devices(
    filter: { labels: $labels, deviceName: $deviceName }
  ) {
    edges {
      node {
        id
        name
        createdAt
        isInstalled
        serviceState
        zone {
          id
          name
        }
      }
    }
  }
} """

device_by_label_template = """
query Devices(
  $labels: [String!]
) {
  devices(
    filter: { labels: $labels }
  ) {
    edges {
      node {
        name
      }
    }
  }
} """

def execute_inventory(body, variables):
    print("Inventory worker", body, variables)
    return client.execute(query=body, variables=variables)


def get_zone_id(zone_name):
    zone_id_device = "query { zones { edges { node {  id name } } } }"

    body = execute_inventory(zone_id_device, '')
    for node in body['data']['zones']['edges']:
        if node['node']['name'] == zone_name:
            return node['node']['id']


def get_all_devices(labels):
    device_id_name = copy.deepcopy(device_by_label_template)
        
    variables = {
        "labels": str(str(labels)),
    }

    body = execute_inventory(device_id_name, variables)
    return body['data']['devices']['edges']


def get_device_info(device_name):

    variables = {
        "deviceName": str(str(device_name)),
    }
    response = execute_inventory(device_info_template, variables)

    # if graphql request fail
    if response.get('errors'):
        return device_name, None, response['errors'][0]['message']

    # if device was found
    for node in response['data']['devices']['edges']:
        if node['node']['name'] == device_name:
            return node['node']['name'], node['node']['id'], node['node']['isInstalled']

    # if device was not found
    return device_name, None, None


def get_label_id():
    label_id_device = "query { labels { edges { node {  id name } } } }"
    body = execute_inventory(label_id_device, '')

    label_id={}
    for node in body['data']['labels']['edges']:
        label_id[node['node']['name']]=node['node']['id']

    return label_id

def create_label(label_name):
    variables = {'input': {
        "name": label_name
    }}
    response = execute_inventory(create_label_template, variables)

    if response['data']['createLabel']['label']['name'] == label_name:
        label_id = response['data']['createLabel']['label']['id']
        return label_id, None
    elif response.get('errors'):
        return None, response['errors'][0]['message']
    else:
        return None, {"Label was not created"}
####################################################################################


def installed_device(task):

    body = {}
    variables = {
        "deviceName": str(str(task['inputData']['device_name'])),
    }

    response = execute_inventory(device_info_template, variables)

    if response.get('errors'):
        body['message'] = response['errors'][0]['message']
        return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                'logs': []}

    if response.get('data'):
        body['name'] = response['data']['devices']['edges']

        return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200, 'response_body': body},
                'logs': []}

    return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': {'Workflow failed'}},
            'logs': []}


def install_uninstall_device(task):

    if str(task['taskType']).find('_by_name') != -1:

        device_name, device_id, device_status = get_device_info(task['inputData']['device_name'])

        if device_id is None:
            body = {"message": device_status}
            return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                    'logs': []}

        variables = {
            "id": str(device_id)
        }

    else:
        variables = {
            "id": str(task['inputData']['device_id'])
        }

    body = {
        'id': str(variables['id'])
    }

    if str(task['taskType']).find('uninstall') == -1:
        # install task

        response = execute_inventory(install_device_template, variables)
        task_type = "installDevice"
    else:
        # uninstall task
        response = execute_inventory(uninstall_device_template, variables)
        task_type = "uninstallDevice"

    if response.get('errors'):
        body['message'] = response['errors'][0]['message']

        if 'already been installed' not in body['message']:
            return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                    'logs': []}

    if response.get('data'):
        body['name'] = response['data'][task_type]['device']['name']

    return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200, 'response_body': body},
            'logs': []}


def install_uninstall_in_batch(task):
    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 
    page_size = int(task['inputData']['page_size'])
    page_id = str(task['inputData']['page_id'])

    # check if labels exist
    if len(label_names)>0:
        # get all label names and ids as dict
        labels_id_name = get_label_id()

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': "Label " + label_name + " not exist" },
                'logs': []}

    variables = {
        "first": int(page_size),
        "after": str(page_id),
        "labels": label_names
    }

    response = execute_inventory(device_page_id_template, variables)

    body = {}
    if response.get('errors'):
        body['message'] = response['errors'][0]['message']
        return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                'logs': []}

    if str(task['taskType']).find('uninstall') == -1:
        # install task
        device_template = install_device_template
        task_type = "installDevice"
    else:
        # uninstall task
        device_template = uninstall_device_template
        task_type = "uninstallDevice"

    device_status = {}
    for device_id in response['data']['devices']['edges']:

        variables = {
            "id": str(device_id['node']['id'])
        }

        response = execute_inventory(device_template, variables)

        per_device_params = dict({})
        per_device_params.update({"device_id": device_id['node']['id']})
        per_device_params.update({"device_name": device_id['node']['name']})

        if task_type is "installDevice":
            if response.get('errors'):
                if 'already been installed' not in response['errors'][0]['message']:
                    per_device_params.update({"status": "failed"})
                elif 'already been installed' in response['errors'][0]['message']:
                    per_device_params.update({"status": "was installed before"})
            elif response.get('data'):
                per_device_params.update({"status": "success"})
        elif task_type is "uninstallDevice":
            if response.get('errors'):
                per_device_params.update({"status": "failed"})
            elif response.get('data'):
                per_device_params.update({"status": "success"})

        device_status.update({device_id['node']['name']: per_device_params})

    return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200, 'response_body': device_status},
            'logs': []}


def get_device_pages_ids(task):
    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 
    device_step = 10
    cursor_count = 20
    has_next_page = True
    page_ids = []
    last_page_id = ''

    print(label_names)
    # check if labels exist
    if len(label_names)>0:
        # get all label names and ids as dict
        labels_id_name = get_label_id()

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': "Label " + label_name + " not exist" },
                'logs': []}

    while has_next_page:
        variables = {
            "first": device_step,
            "after": str(last_page_id),
            "labels": label_names.replace(" ", "")
        }

        response = execute_inventory(device_page_template, variables)
        if response.get('errors'):
            body = {'message': response['errors'][0]['message']}
            return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                    'logs': []}

        if response.get('data'):

            has_next_page = response['data']['devices']['pageInfo']['hasNextPage']

            if response['data']['devices']['pageInfo']['hasPreviousPage'] is False:
                last_page_id = ''
                page_ids.append(last_page_id)

            if has_next_page is not False:
                last_page_id = response['data']['devices']['pageInfo']['endCursor']
                page_ids.append(last_page_id)

            if has_next_page is False:
                break

    page_loop = {}
    for i in range(math.ceil(len(page_ids) / cursor_count)):
        page_loop[i] = []
        for j in range(cursor_count):
            try:
                page_loop[i].append(page_ids[i * cursor_count + j])
            except Exception as e:
                print(e)
                break

    return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200,
                                              'page_ids': page_loop,
                                              'page_size': len(page_loop),
                                              "page_ids_count": len(page_ids)},
            'logs': []}


def page_device_dynamic_fork_tasks(task):
    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 

    task_name = task['inputData']['task']
    page_ids = task['inputData']['page_ids']

    # check if labels exist
    if len(label_names)>0:
        # get all label names and ids as dict
        labels_id_name = get_label_id()

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': "Label " + label_name + " not exist" },
                'logs': []}

    device_step = 40

    dynamic_tasks = []
    dynamic_tasks_i = {}

    taskReferenceName_id = 0
    

    for device_id in page_ids:
        task_body = copy.deepcopy(task_body_template)
        task_body["taskReferenceName"] = "devices_page_" + str(taskReferenceName_id)
        task_body["subWorkflowParam"]["name"] = task_name
        dynamic_tasks.append(task_body)

        per_device_params = dict({})
        per_device_params.update({"page_id": device_id})
        per_device_params.update({"page_size": device_step})
        per_device_params.update({"labels": label_names})
        dynamic_tasks_i.update({"devices_page_" + str(taskReferenceName_id): per_device_params})
        taskReferenceName_id += 1

    return {'status': 'COMPLETED',
            'output': {'url': inventory_url_base, 'dynamic_tasks_i': dynamic_tasks_i, 'dynamic_tasks': dynamic_tasks},
            'logs': []}

def all_devices_fork_tasks(task):

    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 
    task_name = task['inputData']['task']
    add_params = task['inputData']['task_params']
    add_params = json.loads(add_params) if isinstance(add_params, str) else (add_params if add_params else {})
    optional = task['inputData']['optional'] if 'optional' in task['inputData'] else "false"

    # check if labels exist
    if len(label_names)>0:
        # get all label names and ids as dict
        labels_id_name = get_label_id()

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': "Label " + label_name + " not exist" },
                'logs': []}

    ids = get_all_devices(label_names)
  
    dynamic_tasks = []
    dynamic_tasks_i = {}

    for device in ids:
        device_id = device['node']['name']

        task_body = copy.deepcopy(task_body_template)
        if optional == "true": 
            task_body['optional'] = True
        task_body["taskReferenceName"] = device_id 
        task_body["subWorkflowParam"]["name"] = task_name
        dynamic_tasks.append(task_body)

        per_device_params = dict(add_params)
        per_device_params.update({"device_id": device_id})
        dynamic_tasks_i.update({device_id: per_device_params})

    return {'status': 'COMPLETED',
            'output': {'url': inventory_url_base, 'dynamic_tasks_i': dynamic_tasks_i, 'dynamic_tasks': dynamic_tasks},
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
    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 

    variables = {'input': {
        "name": task['inputData']['device_id'],
        "zoneId": get_zone_id(task['inputData']['uniconfig_zone']),
        "serviceState": task['inputData']["service_state"],
        "mountParameters": str(body).replace("'", '"'),
    }}

    if len(label_names)>0:
        labels_id_name = get_label_id()
        label_ids=[]

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                label_id, error = create_label(label_name)
                if error is not NoneType:
                    return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': error},
                    'logs': []}
            label_ids.append(label_id)

        variables['input']['labelIds'] = label_ids

    response = execute_inventory(add_device_template, variables)

    if response.get('errors'):
        body['message'] = response['errors'][0]['message']
        return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                'logs': []}

    body = {
        "id": response['data']['addDevice']['device']['id'],
        "name": response['data']['addDevice']['device']['name'],
        "isInstalled": response['data']['addDevice']['device']['isInstalled']
    }

    return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200, 'response_body': body},
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
    label_names = "" if task['inputData']['labels'] is None else task['inputData']['labels'].replace(" ", "") 

    if "blacklist" in task["inputData"] and task["inputData"]["blacklist"] is not NoneType:
        model_array = [model.strip() for model in task["inputData"]["blacklist"].split(",")]
        for model in model_array:
            body["netconf"]["uniconfig-config:blacklist"]["uniconfig-config:path"].append(model)

    variables = {'input': {
        "name": task['inputData']['device_id'],
        "zoneId": get_zone_id(task['inputData']['uniconfig_zone']),
        "serviceState": task['inputData']["service_state"],
        "mountParameters": str(body).replace("'", '"'),
    }}

    if len(label_names)>0:
        labels_id_name = get_label_id()
        label_ids=[]

        # check if all input labels exist
        for label_name in label_names.split(","):
            label_id=labels_id_name.get(label_name)
            if label_id == None:
                label_id, error = create_label(label_name)
                if error is not NoneType:
                    return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': error},
                    'logs': []}
            label_ids.append(label_id)

        variables['input']['labelIds'] = label_ids

    response = execute_inventory(add_device_template, variables)

    if response.get('errors'):
        body['message'] = response['errors'][0]['message']
        return {'status': 'FAILED', 'output': {'url': inventory_url_base, 'response_code': 404, 'response_body': body},
                'logs': []}

    body = {
        "id": response['data']['addDevice']['device']['id'],
        "name": response['data']['addDevice']['device']['name'],
        "isInstalled": response['data']['addDevice']['device']['isInstalled']
    }

    return {'status': 'COMPLETED', 'output': {'url': inventory_url_base, 'response_code': 200, 'response_body': body},
            'logs': []}


def start(cc):
    print('Starting Inventory workers')

    cc.register('INVENTORY_get_devices_info', {
        "description": '{"description": "Get information about devices in inventory by device name", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "inputKeys": [
            "device_name"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, installed_device)

    cc.register('INVENTORY_get_all_devices_as_dynamic_fork_tasks', {
        "description": '{"description": "Get all devices as dynamic fork task", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "inputKeys": [
            "labels",
            "task",
            "task_params",
            "optional"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    }, all_devices_fork_tasks)

    cc.register('INVENTORY_install_device_by_name', {
        "description": '{"description": "Install device by device name", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "device_name"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_uninstall_device_by_name', {
        "description": '{"description": "Uninstall device by device name", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "device_name"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_install_device_by_id', {
        "description": '{"description": "Install device by device ID", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
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
        "description": '{"description": "Uninstall device by device ID", "labels": ["BASICS","INVENTORY"]}',
        "timeoutSeconds": 3600,
        "responseTimeoutSeconds": 3600,
        "inputKeys": [
            "device_id"
        ],
        "outputKeys": [
            "url",
            "response_code",
            "response_body"
        ]
    }, install_uninstall_device)

    cc.register('INVENTORY_get_pages_cursors_fork_tasks', {
        "name": "INVENTORY_get_pages_cursors_fork_tasks",
        "description": '{"description": "get all pages cursors as dynamic fork tasks", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "task",
            "page_ids"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    }, page_device_dynamic_fork_tasks)

    cc.register('INVENTORY_install_in_batch', {
        "name": "INVENTORY_install_in_batch",
        "description": '{"description": "install devices in batch started from page cursor", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "labels",
            "page_id",
            "page_size"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    }, install_uninstall_in_batch)

    cc.register('INVENTORY_uninstall_in_batch', {
        "name": "INVENTORY_uninstall_in_batch",
        "description": '{"description": "uninstall devices in batch started from page cursor", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [
            "page_id",
            "page_size",
            "labels"
        ],
        "outputKeys": [
            "url",
            "dynamic_tasks_i",
            "dynamic_tasks"
        ]
    }, install_uninstall_in_batch)

    cc.register('INVENTORY_get_pages_cursors', {
        "name": "INVENTORY_get_pages_cursors",
        "description": '{"description": "get a list of pages cursors from device inventory", "labels": ["BASICS","INVENTORY"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
        "inputKeys": [],
        "outputKeys": [
            "labels",
            "url",
            "response_code",
            "page_ids_count",
            'page_size',
            "page_ids",
        ]
    }, get_device_pages_ids)

    cc.register('INVENTORY_add_cli_device', {
        "description": '{"description": "add a CLI device to inventory database", "labels": ["BASICS","MAIN","INVENTORY","CLI"]}',
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
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
        "responseTimeoutSeconds": 3600,
        "timeoutSeconds": 3600,
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
