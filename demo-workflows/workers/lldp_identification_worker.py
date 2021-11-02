import util
import logging
import re
import copy

local_logs = logging.getLogger(__name__)

odl_url_get_installed_nodes = "$base_url/operations/connection-manager:get-installed-nodes"

lldp_info_template = {
    "neighbor_device_name": "",
    "local_interface": "",
    "neighbor_interface": "",
}

def lldp_input_validation(task):
    DEVICE_SOFTWARES = ["saos", "ios xr"]
    device_name = task["inputData"]["device_name"]
    device_software = task["inputData"]["device_software"]

    if not device_name:
        return util.failed_response({"Error": "Device name is missing"})

    if device_software not in DEVICE_SOFTWARES:
        return util.failed_response({"Error": "Wrong device software. Please select one of these device softwares [saos, ios xr]"})

    return util.completed_response({'device_name': device_name, "sw":device_software})


def read_and_parse_rpc_cli_saos_6_and_8(task):
    """ Parse RPC output from Ciena Saos6/8 device, check it's LLDP
    neighbors, extract and return relevant LLDP data.

    Args:
        task (dict): Has to contain key device_name.

    Returns:
        dict: Standard worker response with operation status
              along with list of dicts containing LLDP data.
    """

    rpc_input = task["inputData"]["rpc_input"]
    lldp_config = []

    interfaces_pattern_matching = list(
        filter(re.compile(r"^\|[0-9]").match, rpc_input.split("\r\n"))
    )
    device_pattern_matching = list(
        filter(re.compile(r"^\|.*\| System Name").match, rpc_input.split("\r\n"))
    )

    for interfaces, name in zip(interfaces_pattern_matching, device_pattern_matching):
        lldp_info = copy.deepcopy(lldp_info_template)
        (
            lldp_info["local_interface"],
            lldp_info["neighbor_interface"],
        ) = interfaces.replace(" ", "").split("|")[1:-2]
        lldp_info["neighbor_device_name"] = name[name.find(":") + 1 : -1].replace(
            " ", ""
        )
        lldp_config.append(lldp_info)

    return util.completed_response({"lldp_config": lldp_config})


def parse_netconf_data_iosxr(task):
    """ Parse LLDP structured data obtained from an IOS XR device.
    Parse the neighbors of the device, return interfaces

    Args:
        task (dict): Has to contain key netconf_data

    Returns:
        dict: List of interfaces
    """
    netconf_data = task["inputData"]["netconf_data"]

    lldp_entries = netconf_data['lldp']['nodes']['node']

    lldp_config = []
    for entry in lldp_entries:
        neighbor_key = "neighbors"
        if neighbor_key in entry:
            neighbors = entry["neighbors"]["details"]["detail"]
        else:
            continue

        for neighbor in neighbors:
            for lldp_neighbor in neighbor["lldp-neighbor"]:
                lldp_info = copy.deepcopy(lldp_info_template)
                try:
                    lldp_info["neighbor_device_name"] = lldp_neighbor['device-id']
                    lldp_info["neighbor_interface"] = lldp_neighbor['port-id-detail']
                    lldp_info["local_interface"] = lldp_neighbor['receiving-parent-interface-name']
                    lldp_config.append(lldp_info)
                except:
                    pass

    return util.completed_response({"lldp_config": lldp_config})



def start(cc):
    local_logs.info("Starting lldp workers")

    cc.register(
        "LLDP_input_validation",
        {
            "description": '{"description": "Validate LLDP input}',
            "inputKeys": ["device_name", "sw"],
            "outputKeys": ["lldp_config"],
        }
        , lldp_input_validation
    )

    cc.register(
        "LLDP_read_and_parse_rpc_cli_saos_6_and_8",
        {
            "description": '{"description": "Parse RPC LLDP output and return sensible structured data.", "labels": ["LLDP"]}',
            "inputKeys": ["rpc_input"],
            "outputKeys": ["lldp_config"],
        }
        , read_and_parse_rpc_cli_saos_6_and_8
    )
    cc.register(
        "LLDP_parse_netconf_iosxr",
        {
            "description": '{"description": "Parse LLDP output of netconf for IOS XR devices", "labels": ["LLDP"]}',
            "inputKeys": ["netconf_data"],
            "outputKeys": ["lldp_config"],
        }
        , parse_netconf_data_iosxr)