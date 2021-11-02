from uuid import uuid1
from marshmallow import ValidationError
import util
from worker_helpers.device_worker_helper import NETCONF_MOUNT_BODY, get_device_model, SCHEMA_BLACKLIST, NETCONF_URI_DICT
from frinx_conductor_workers import netconf_worker
from validation.device_identification import DeviceIdentificationSchema
import re
import copy
import time




def validate_input_parameters_device_identification(task):
    """
    Validate user inputs in WF
    :param task: a dict with the following structure:
            "inputData": {
                'port': '10000',
                }
    :return: {"response_body": "Input parameters are valid"}
    """
    input_parameters = task["inputData"]
    schema = DeviceIdentificationSchema()
    try:
        schema.load(input_parameters)
    except ValidationError as err:
        return util.failed_response(err.messages)
    return util.completed_response(
        {"response_body": "Input parameters are valid"})


def create_unique_device_name(task):
    device_name = "Device" + str(uuid1().hex)
    return util.completed_response({'device_name': device_name})


def mount_netconf_device_identification(task):
    devices = {"cisco-ios-xr-653": {"device_id": task["inputData"]["device_id"] + "cisco653",
                                    "config": {"blacklist": ",".join(SCHEMA_BLACKLIST["cisco-ios-xr"]),
                                               "schema-cache-directory": "cisco-iosxr-653"}},
               "cisco-ios-xr-663": {"device_id": task["inputData"]["device_id"] + "cisco663",
                                    "config": {"blacklist": ",".join(SCHEMA_BLACKLIST["cisco-ios-xr"]),
                                               "schema-cache-directory": "cisco-iosxr-663"}},
               "juniper": {"device_id": task["inputData"]["device_id"] + "juniper",
                           "config": {"schema-cache-directory": "junos-16-2021"}}
               }


    task["inputData"].update(NETCONF_MOUNT_BODY)
    mounted_device = {}
    for device_type, device in devices.items():
        updated_task = copy.deepcopy(task)
        updated_task["inputData"]["device_id"] = device["device_id"]
        if "config" in device:
            updated_task["inputData"].update(device["config"])
        mount_res = netconf_worker.execute_mount_netconf(updated_task)

        if mount_res["status"] == util.COMPLETED_STATUS:
            device_dict = NETCONF_URI_DICT[device_type]

            response = netconf_worker.read_structured_data({"inputData": {"device_id": device["device_id"],
                                                        "uri": device_dict['uri']['version']}})
            if response['status'] == 'COMPLETED' and response["output"]["response_code"] == 200:
                sw_version = list(response["output"]["response_body"].values())[0]
                mounted_device = {"mounted_device_id": device["device_id"],
                                  "device_type": device_type,
                                  "sw_version": sw_version}
                break

    return util.completed_response(mounted_device)


def identification_of_netconf_device(task):
    device_dict = NETCONF_URI_DICT[task["inputData"]["device_type"]]
    # Read data with netconf or uniconfig based on topology

    result_dict = {"version": task["inputData"]["sw_version"]}
    for _ in range(20):
        for field, uri in device_dict['uri'].items():
            if field not in result_dict:
                task["inputData"]["uri"] = uri
                response = netconf_worker.read_structured_data(task)
                if response['status'] == 'COMPLETED' and response["output"]["response_code"] == 200:
                    result_dict[field] = list(response["output"]["response_body"].values())[0]
        if device_dict['uri'].keys() == result_dict.keys():
            break
        time.sleep(2)

    netconf_worker.execute_unmount_netconf({"inputData": {"device_id": task["inputData"]["device_id"]}})

    response_body = {
        "device_name": result_dict.get("hostname", ""),
        "device_sw": device_dict["details"]["sw"],
        "device_version": result_dict.get("version", ""),
        "device_vendor": device_dict["details"]["vendor"],
        "device_model": result_dict.get("model", "")
    }
    return util.completed_response({"response_body": response_body})


def ip_address_identification(task):
    device_data = task["inputData"]["device_data"]
    device_name = ""
    device_version = ""
    device_sw = ""
    device_vendor = ""
    device_model = ""
    cisco_has_role = False

    device_data = device_data.split("\r\n")
    for line in device_data:
        ciena_device_regex = re.search(r"! SW Package:", str(line))
        ciena_device_name_regex = re.search(r"! Host Name:\s+(\S+)", str(line))
        cisco_device_regex = re.search(r"^Cisco", str(line))
        cisco_device_name_regex = re.search(r"hostname (\S+)", str(line))
        juniper_device_name_regex = re.search(r"Hostname: (\S+)", str(line))
        juniper_sw_version_regex = re.search(r"Junos: (\d\S+)", str(line))
        if not device_model or device_model.endswith("x"):
            device_model = get_device_model(line, device_model)

        if juniper_sw_version_regex:
            device_version = juniper_sw_version_regex.group(1)
            device_sw = "juniper"
            device_vendor = "juniper"

        if juniper_device_name_regex:
            device_name = juniper_device_name_regex.group(1)

        if ciena_device_name_regex:
            device_name = ciena_device_name_regex.group(1)

        elif ciena_device_regex and not device_version:
            device_sw = "saos"
            device_vendor = "ciena"
            is_saos8 = re.search(r"! SW Package:\s+rel_saos8700", str(line))
            is_saos8_2 = re.search(r"! SW Package:\s+rel_saos5170", str(line))
            is_saos6 = re.search(r"! SW Package:\s+Slot 1 - saos-06", str(line))
            if is_saos6:
                device_version = "6"
            elif is_saos8 or is_saos8_2:
                device_version = "8"

        elif cisco_device_regex and not cisco_has_role:
            device_vendor = "cisco"
            device_version_regex = re.search(r"Version (\d+\.\d+\.\d+|\d+\.\d+)", str(line))
            device_version = device_version_regex.group(1)
            is_ios_xr = re.search(r"Cisco IOS XR Software", str(line))
            is_ios_xe = re.search(r"Cisco IOS XE Software", str(line))
            is_ios = re.search(r"Cisco IOS Software", str(line))
            cisco_has_role = True
            if is_ios:
                device_sw = "ios"
            elif is_ios_xe:
                device_sw = "ios xe"
            elif is_ios_xr:
                device_sw = "ios xr"

        elif cisco_device_name_regex:
            device_name = cisco_device_name_regex.group(1)


    response_body = {
        "device_name": device_name,
        "device_sw": device_sw,
        "device_version": device_version,
        "device_vendor": device_vendor,
        "device_model": device_model
    }
    return util.completed_response({"response_body": response_body})


def start(cc):
    cc.register('Device_identification_validate_input_parameters', {
        "description": '{"description": "Validate input parameters for device identification}',
        "timeoutSeconds": 60,
        "retryCount": 0,
        "timeoutPolicy": "TIME_OUT_WF",
        "retryLogic": "FIXED",
        "retryDelaySeconds": 0,
        "responseTimeoutSeconds": 10,
        "inputKeys": [
            "port"
        ],
        "outputKeys": [
            "response_body",
            "error_message"
        ]
    }, validate_input_parameters_device_identification)

    cc.register('Create_unique_device_name', {
        "description": '{"description": "Create unique device name"}',
        "inputKeys": [],
        "outputKeys": [
            "device_name"
        ]
    }, create_unique_device_name)

    cc.register('Mount_netconf_device_identification', {
        "description": '{"description": "Identify type of netconf device and mount with correct schema"}',
        "timeoutSeconds": 600,
        "responseTimeoutSeconds": 600,
        "inputKeys": [
            "device_id",
            "host",
            "port",
            "username",
            "password"
        ],
        "outputKeys": [
            "device_type",
            "mounted_device_id",
            "sw_version"
        ]
    }, mount_netconf_device_identification)


    cc.register('Identification_of_device', {
        "description": '{"description": "Identification of device"}',
        "inputKeys": [
            "device_data",
        ],
        "outputKeys": [
            "response_body"
        ]
    }, ip_address_identification)

    cc.register('Identification_of_netconf_device', {
        "description": '{"description": "Identificate netconf device data"}',
        "retryCount": 4,
        "timeoutSeconds": 120,
        "responseTimeoutSeconds": 60,
        "inputKeys": [
            "device_type"
        ],
        "outputKeys": [
            "response_body"
        ]
    }, identification_of_netconf_device)
