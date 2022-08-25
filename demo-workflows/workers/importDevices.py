#!/usr/bin/env python3

from collections import namedtuple
from sys import argv
from python_graphql_client import GraphqlClient
import os
from frinx_conductor_workers.frinx_rest import x_tenant_id, inventory_url_base

# graphql client settings
inventory_headers = {
    "Accept-Encoding": "gzip, deflate, br",
    "Content-Type": "application/json",
    "Accept": "application/json",
    "Connection": "keep-alive",
    "x-tenant-id": x_tenant_id,
    "DNT": "1"
}

client = GraphqlClient(endpoint=inventory_url_base, headers=inventory_headers)


def execute(body, variables):
    response = client.execute(query=body, variables=variables)
    if response.get('errors'):
        print("IMPORT DEVICES:", response)
    return response

install_device_template = """ 
mutation  AddDevice($input: AddDeviceInput!) {
    addDevice(input: $input) {
        device {
            id
            name
            isInstalled
        }
    }
} """

create_blueprint_template = """
mutation AddBlueprint($input: AddBlueprintInput!) {
  addBlueprint(input: $input) {
    blueprint {
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


def main():
    DEVICE_DATA_CSV = argv[1]
    DEVICE_DATA_JSON = argv[2]

    import_devices(DEVICE_DATA_CSV, DEVICE_DATA_JSON)
    import_blueprints(DEVICE_DATA_JSON)

def get_zone_id(zone_name):
    zone_id_device = "query { zones { edges { node {  id name } } } }"

    body = execute(zone_id_device, '')

    for node in body['data']['zones']['edges']:
        if node['node']['name'] == zone_name:
            return node['node']['id']


def get_label_id(label_name):
    zone_id_device = "query { labels { edges { node {  id name } } } }"

    label_id = ''
    body = execute(zone_id_device, '')
    for node in body['data']['labels']['edges']:
        if node['node']['name'] == label_name:
            label_id = node['node']['id']

    if label_id == '':
        variables = {'input': {
            "name": label_name
        }}
        response = execute(create_label_template, variables)
        if response['data']['createLabel']['label']['name'] == label_name:
            label_id = response['data']['createLabel']['label']['id']
            return label_id
    else:
        return label_id

def import_blueprints(device_data_json):

    with open(device_data_json) as json_file:
        device_import_json = json_file.read()

    variables = {'input': {
        "name": device_data_json.split("/")[-1].replace("_import.json",""),
        "template": device_import_json
    }}

    execute(create_blueprint_template, variables)

def import_devices(device_data_csv, device_data_json):
    # definition of replacements in the DEVICE_DATA_JSON file
    json_replacements = {}

    with open(device_data_json) as json_file:
        device_import_json = json_file.read()

    with open(device_data_csv) as data_file:
        all_device_data = data_file.readlines()

    # set header and remove space characters from all elements
    device_data_header = all_device_data[0].split(',')
    for i in enumerate(device_data_header):
        device_data_header[i[0]] = i[1].strip()

    # create a device_data_def suitable for both cli and netconf device types
    device_data_def = namedtuple('device_data_def', device_data_header)

    # create replacements
    for i in device_data_header:
        key = '{{%s}}' % i
        json_replacements[key] = i

    # skip the first line in csv
    all_device_data = all_device_data[1:]

    for device in all_device_data:

        # prepare a list with device data
        data_list = device.strip().split(',')

        # create a dict for easier use
        device_data_tuple = device_data_def(*data_list)
        device_data = dict(device_data_tuple._asdict())

        # Check if device is simulated if not skip adding device into device inventory
        if not _is_simulated(device_data):
            continue

        # copy the postman collections json
        device_json = device_import_json

        # replace the relevant parts for each device to create a JSON file
        for k in json_replacements.keys():
            val = json_replacements[k]
            device_json = device_json.replace(k, device_data[val])

        variables = {'input': {
            "mountParameters": device_json,
            "zoneId": get_zone_id(device_data["zone_name"]),
            "name": device_data["device_id"],
            "serviceState": device_data["service_state"]
        }}

        if not device_data['labels'] == '':
            label_ids=[]
            for label_name in device_data['labels'].split("|"):
                label_ids.append(get_label_id(label_name))

            variables['input']['labelIds'] = label_ids

        response = execute(install_device_template, variables)
        print(response)


def _is_simulated(device_data: dict) -> bool:
    """
    INSTANCES_TO_SIMULATE - string with simulated netconf instances divided by ',' ex. "IOSXR653,IOSXR663,JUNOS,"
    RUN_TESTTOOLS - Use to detect what type of devices are simulated NETCONF, CLI or both of them
    ex. ./scripts/run_netconf_devices/run_netconf_testtool.sh & ./scripts/run_cli_devices/run_devices_docker.sh

    - Check if device type (CLI, NETCONF) is simulated if not -> Return False
    - Check if netconf device is simulated if not -> Return False
    """
    all_instances = "IOSXR653,IOSXR663,JUNOS,"
    instance_to_simulate = all_instances if not os.getenv("INSTANCES_TO_SIMULATE") else os.getenv("INSTANCES_TO_SIMULATE")
    run_testtools = os.getenv("RUN_TESTTOOLS")

    for label in device_data["labels"].split("|"):
        if label.lower() in run_testtools:
            if "netconf" in label.lower():
                device_base_name = device_data["device_id"].split("_")[0]
                if device_base_name not in instance_to_simulate:
                    return False
            return True
    return False

if __name__ == '__main__':
    main()
