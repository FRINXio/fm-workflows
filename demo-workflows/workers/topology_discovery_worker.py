import json
import os

import requests
from frinx_conductor_workers.frinx_rest import (
    additional_uniconfig_request_params, uniconfig_url_base)

import util

TOPOLOGY_DISCOVERY_BASE_URL = "http://topology-discovery:5000/api"
TOPOLOGY_DISCOVERY_HEADERS = {
    "Content-Type": "application/json",
    "X-Auth-User-Roles": "admin-1",
}
MOCK_UNICONFIG_URL_BASE = os.getenv("MOCK_UNICONFIG_URL_BASE")


def sync_physical_devices(task):
    """Call TD endpoint /providers/physical/sync to sync devices in topology discovery
    devices: list (list of devices to sync devices must be installed in UC, ignored when param `sync_all_installed_devices` = True)
    labels: list (stored only when sync_all_installed_devices = False)
    sync_all_installed_devices: bool (if true then sync all devices installed in UC else sync inputted devices)
    To use mock uniconfig change in fm-workflow composefile env to MOCK_UNICONFIG_URL_BASE=http://uniconfig_mock:1080
    """
    devices = task["inputData"]["devices"]
    labels = task["inputData"]["labels"]
    sync_all_installed_devices = int(task["inputData"]["sync_all_installed_devices"])
    data = {}
    # If there is MOCK_UNICONFIG_URL_BASE in composefile use mock uniconfig to get installed devices
    if MOCK_UNICONFIG_URL_BASE != "none":
        uc_url = MOCK_UNICONFIG_URL_BASE
    else:
        uc_url = uniconfig_url_base

    if sync_all_installed_devices:
        installed_nodes_response = requests.post(
            uc_url + "/operations/connection-manager:get-installed-nodes",
            **additional_uniconfig_request_params
        )
        devices = installed_nodes_response.json()["output"]["nodes"]
    else:
        try:
            devices = devices.split(",")
            labels = labels.split(",")
            data["labels"] = labels
        except:
            return util.failed_response(
                {
                    "error_message": "incorrect format for devices/labels please see ex. device1,device2,device3"
                }
            )

    data["devices"] = devices
    sync_response = requests.post(
        TOPOLOGY_DISCOVERY_BASE_URL + "/providers/physical/sync",
        data=json.dumps(data),
        headers=TOPOLOGY_DISCOVERY_HEADERS,
    )

    return util.completed_response(sync_response.json())


def create_backup(task):
    """Create DB backup for topology discovery"""
    response = requests.post(TOPOLOGY_DISCOVERY_BASE_URL + "/data/backup")
    return util.completed_response(response.json())


def delete_backups(task):
    """Delete backup for topology discovery
    delete_age: int (delete all backups which are older than delete_age in hours"""
    delete_age = task["inputData"]["delete_age"]
    data = {"delete_age": int(delete_age)}
    response = requests.delete(
        TOPOLOGY_DISCOVERY_BASE_URL + "/data/backup",
        data=json.dumps(data),
        headers=TOPOLOGY_DISCOVERY_HEADERS,
    )

    return util.completed_response(response.json())


def start(cc):
    cc.register(
        "td_sync_physical_devices",
        {
            "description": '{"description": "Sync all installed physical devices in topology discovery"}',
            "inputKeys": ["devices"],
            "outputKeys": ["loaded_devicse", "labels"],
        },
        sync_physical_devices,
    )

    cc.register(
        "td_create_backup",
        {
            "description": '{"description": "create backup for topology discovery"}',
            "inputKeys": [],
            "outputKeys": ["db_name"],
        },
        create_backup,
    )

    cc.register(
        "td_delete_backups",
        {
            "description": '{"description": "delete all backups which are older than param delete_age in topology discovery"}',
            "inputKeys": ["delete_age"],
            "outputKeys": ["deleted_backups"],
        },
        delete_backups,
    )
