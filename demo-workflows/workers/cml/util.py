import requests

BASE_URL = "https://147.75.87.193/api/v0"
CREDENTIAL = {}
LAB_ID = "414f6afb-6757-4cf7-9ac3-d2848d48db89"
UBUNTU_NODE_CONFIGURATION = "#cloud-config\nhostname: inserthostname_here\nmanage_etc_hosts: True\nsystem_info:\n  default_user:\n    name: dtw\npassword: dtw2022\nchpasswd: {{ expire: False }}\nssh_pwauth: True\nssh_authorized_keys:\n   - your-ssh-pubkey-line-goes-here\nwrite_files:\n - path: /etc/netplan/50-cloud-init.yaml\n   content: |\n    network:\n      ethernets:\n        eth0:\n          addresses:\n            - {ip_address}/24\n          gateway4: 192.168.253.1\n          dhcp4: false\n      version: 2\nruncmd:\n  - sudo netplan apply\n  - sudo docker run -itd --privileged --net=host --name arcos arcos_20220816"



NODE_CONFIG = {
    "x": 900,
    "y": 400,
    "label": "",
    "configuration": "",
    "node_definition": "mecubuntu",
    "image_definition": None,
    "cpu_limit": 100,
    "data_volume": 0,
    "boot_disk_size": 0,
    "hide_links": False,
    "tags": [],
    "ram": 8192,
    "cpus": 4
}


class BearerToken:
    @staticmethod
    def get_bearer_token() -> str:
        """ Return token as a str ex.  "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9" """
        response = requests.post(BASE_URL + "/authenticate", json=CREDENTIAL)
        if response.status_code != 200:
            raise Exception(f"Token cannot be created. Response: {response.json()}")
        return response.json()

    @staticmethod
    def deactivate_bearer_token(token: str) -> int:
        """ Return status code: 200 if token was deactivated, 401 if token not exist """
        headers = {"Authorization": f"Bearer {token}"}
        response = requests.delete(BASE_URL + "/logout?clear_all_sessions=false", headers=headers)
        return response.status_code

