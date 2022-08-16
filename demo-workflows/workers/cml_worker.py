import util
from cml.util import BearerToken
from cml.create_and_run_node import CreateAndRunNode
from cml.create_link_between_interfaces import CreateLinkBetweenInterfaces


def create_cml_node(task):
    x, y = task["inputData"]["position"].split(",")
    node_name = task["inputData"]["node_name"]
    ip_address = task["inputData"]["ip_address"]
    token = BearerToken.get_bearer_token()

    try:
        created_node = CreateAndRunNode(node_name, int(x), int(y), ip_address, token)
    except Exception as e:
        BearerToken.deactivate_bearer_token(token)
        return util.failed_response(str(e))

    BearerToken.deactivate_bearer_token(token)
    return util.completed_response({"node_id": created_node.node_id})


def create_link_between_unmanaged_switch_and_created_node(task):
    node_id = task["inputData"]["node_id"]
    token = BearerToken.get_bearer_token()

    try:
        created_link = CreateLinkBetweenInterfaces(node_id, token)
    except Exception as e:
        BearerToken.deactivate_bearer_token(token)
        return util.failed_response(str(e))

    BearerToken.deactivate_bearer_token(token)
    return util.completed_response({"link_id": created_link.link_id})


def generate_ip(task):
    return util.completed_response({"ip_address": "192.168.253.101"})


def start(cc):

    cc.register('CREATE_cml_node', {
        "description": '{"description": "Create and run cml node"}',
        "inputKeys": [
            "node_name"
        ],
        "outputKeys": [
            "node_id",
            "erro_msg"
        ]
    }, create_cml_node)

    cc.register('CREATE_link_between_unmanaged_switch_and_created_node', {
        "description": '{"description": "Create link"}',
        "inputKeys": [
            "node_id"
        ],
        "outputKeys": [
            "link_id",
            "erro_msg"
        ]
    }, create_link_between_unmanaged_switch_and_created_node)


    cc.register('GENERATE_ipaddress', {
        "description": '{"description": "Create link"}',
        "inputKeys": [],
        "outputKeys": [
            "ip_address"
        ]
    }, generate_ip)