import requests
from cml.util import NODE_CONFIG, BASE_URL, UBUNTU_NODE_CONFIGURATION, LAB_ID


class CreateAndRunNode:
    def __init__(self, node_name: str, x, y,ip_address: str ,token: str):
        self.lab_id = LAB_ID
        self.ip_address = ip_address
        self.node_name = node_name
        self.headers = {"Authorization": f"Bearer {token}"}

        self.node_id = self.create_node(x, y)
        self.update_node_config()
        self.run_node()

    def create_node(self,x: int, y: int) -> str:
        """ Return ex. : "c1624ab-6ac3-476d-805c-180270407022" """
        NODE_CONFIG["label"] = self.node_name
        NODE_CONFIG["x"] = x
        NODE_CONFIG["y"] = y
        create_node_endpoint = f"/labs/{self.lab_id}/nodes?populate_interfaces=true"
        response = requests.post(BASE_URL + create_node_endpoint, json=NODE_CONFIG, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Node cannot be created. Response: {response.json()}")
        return response.json().get("id")

    def update_node_config(self):
        """ Update node configuration part before run """
        update_node_endpoint = f"/labs/{self.lab_id}/nodes/{self.node_id}"
        configuration = {"configuration": UBUNTU_NODE_CONFIGURATION.format(hostname=self.node_name,ip_address=self.ip_address)}
        response = requests.patch(BASE_URL + update_node_endpoint, json=configuration, headers=self.headers)

        if response.status_code != 200:
            raise Exception(f"Node configuration cannot be updated. Response: {response.json()}")
        return {"status": f"configuration updated: {UBUNTU_NODE_CONFIGURATION.format(ip_address=self.ip_address)}"}

    def run_node(self) -> dict:
        run_node_endpoint = f"/labs/{self.lab_id}/nodes/{self.node_id}/state/start"
        response = requests.put(BASE_URL + run_node_endpoint, headers=self.headers)
        if response.status_code != 204:
            raise Exception(f"Node cannot be run due to: {response.json()}")
        return {"status": "running"}
