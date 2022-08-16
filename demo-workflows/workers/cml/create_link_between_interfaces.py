import requests
from cml.util import BASE_URL, LAB_ID


class CreateLinkBetweenInterfaces:
    def __init__(self, node_id: str, token: str):
        self.node_id = node_id
        self.headers = {"Authorization": f"Bearer {token}"}

        self.lab_topology = requests.get(BASE_URL + f"/labs/{LAB_ID}/topology/", headers=self.headers).json()

        unmanaged_switch_details = self.get_unmanaged_switch_details()
        node_details = self.get_node_details()

        unmanaged_switch_interface = self.get_available_interface_in_node(unmanaged_switch_details)
        node_interface = self.get_available_interface_in_node(node_details)

        self.link_id = self.create_link(node_interface["id"], unmanaged_switch_interface["id"])

    def get_unmanaged_switch_details(self) -> dict:
        """
        - Search in topology for first found unmanaged switch node
        - Return dict with details of unmanaged_switch

        Raise exception if there is no unmanaged switch in lab
        """
        unmanaged_switch = None
        for node in self.lab_topology["nodes"]:
            if node["node_definition"] == "unmanaged_switch":
                unmanaged_switch = node
                break
        if not unmanaged_switch:
            raise Exception(f"There is no unmanaged switch in this lab topology {self.lab_topology['nodes']}")

        return unmanaged_switch

    def get_node_details(self) -> dict:
        """ Return node details from lab topology by specified node id"""
        node_details = None
        for node in self.lab_topology["nodes"]:
            if node["id"] == self.node_id:
                node_details = node
                break

        if not node_details:
            raise Exception(f"No node id {self.node_id} found in lab topology: {self.lab_topology}")
        return node_details

    def get_available_interface_in_node(self, node_details: dict) -> dict:
        """ Return first found available interface in node details dict """
        available_interface = None
        for interface in node_details["interfaces"]:
            interface_endpoint = f"/labs/{LAB_ID}/interfaces/{interface['id']}"
            interface_data = requests.get(BASE_URL + interface_endpoint, headers=self.headers).json()

            if interface_data["state"] in ["STARTED", "DEFINED_ON_CORE"] and interface_data["is_connected"] is False:
                available_interface = interface
                break
        if not available_interface:
            raise Exception(f"There is not available interface in node: {node_details['label']}, details: {node_details}")

        return available_interface

    def create_link(self, src_interface: str, dst_interface: str):
        """ Create link between src_interface (created node) and dst_interface (unmanaged switch), Return link id """
        create_link_endpoint = f"/labs/{LAB_ID}/links"
        json_body = {"src_int": src_interface, "dst_int": dst_interface}
        response = requests.post(BASE_URL + create_link_endpoint, json=json_body, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Link cannot be created, details: {response.json()}")
        return response.json()
