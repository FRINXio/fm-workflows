from ncclient import manager
from ncclient.xml_ import to_ele
from pathlib import Path
import os
import socket
import time


DIR_PATH = Path(os.path.dirname(os.path.realpath(__file__)))


class NetconfAddConfigs:
    def __init__(self):
        with open(str(Path(DIR_PATH,'netconf_devices.txt'))) as f:
            self.devices = f.read().splitlines()

    def run(self):
        """
        For every netconf device:
        - check if connection to device is available
        - push config data to device
        - push operation data to device
        """
        devices_status = {"updated_devices": [], "skipped_devices": []}
        for device in self.devices:
            # device ex. 'iosxr653_1 17000' extract name & port
            device_name, port = device.split(" ")
            # Check if device is available
            print("Trying connect to a device {}".format(device_name))
            if not NetconfAddConfigs.is_device_available(os.getenv('DOCKER_GWBRIDGE_IP'), port, device_name):
                print("Cannot connect to a device {}".format(device_name))
                devices_status["skipped_devices"].append(device_name)
                continue
            print("Updating config for device {}".format(device_name))

            # Get and push config file to device
            config_file = NetconfAddConfigs.get_config_file_path(device_name)
            if self.push_config_to_device(port, config_file):
                devices_status["updated_devices"].append(device_name)
            else:
                devices_status['skipped_devices'].append(device_name)
                print("Failed updating config for device {}".format(device_name))
            print("Successfully updated devices: {}".format(devices_status["updated_devices"]))
            print("Failed to update devices: {}".format(devices_status["skipped_devices"]))

            # Get and push operation data to device
            operation_data_list = NetconfAddConfigs.get_operation_files_path(device_name)
            for operation_data in operation_data_list:
                print("pushing operation data: {}".format(str(operation_data)))
                self.push_operation_data_to_device(port, operation_data)

            print("Finished pushing config & operation data into netconf devices!")
    @staticmethod
    def get_config_file_path(device_name):
        config_files_path = Path(DIR_PATH, "..", "..", "configs", "netconf").rglob('config.xml')
        try:
            config_file = [x for x in config_files_path if device_name in str(x)][0]
        except:
            print("{} config file (config.xml) cannot be founded in /configs/netconf".format(device_name))
            return None

        print("Config file: {}".format(str(config_file)))
        return config_file

    @staticmethod
    def get_operation_files_path(device_name):
        operation_files_path = Path(DIR_PATH, "..", "..", "configs", "netconf").rglob('*.xml')
        try:
            operation_files = [x for x in operation_files_path if device_name in str(x) if "config.xml" not in str(x)]
        except:
            print("{} operation data cannot be founded in /configs/netconf".format(device_name))
            return None
        return operation_files

    def push_config_to_device(self, port, config_file):
        print("DEVICE PORT: {}".format(str(port)))
        m = manager.connect(host="sample-topology", port=port, username="frinx",
                            password="frinx", hostkey_verify=False)

        netconf_config = open(str(config_file)).read()
        edit_config = m.edit_config(netconf_config, target="candidate")
        m.commit()

        print(edit_config)
        m.close_session()
        if "ok" in str(edit_config):
            return True
        else:
            return False

    def push_operation_data_to_device(self, port, operation_data):
        m = manager.connect(host="sample-topology", port=port, username="frinx",
                            password="frinx", hostkey_verify=False)

        netconf_operation_data = open(str(operation_data)).read()
        netconf_operation_data = to_ele(netconf_operation_data)

        edit_oper = m.dispatch(to_ele(netconf_operation_data))
        m.commit()

        print(edit_oper)
        m.close_session()


    @staticmethod
    def is_device_available(ip, port, device_name="unknown", attempts=1080):
        """
        Try connect to a device if its running
        There is default 1080 attempts (which is around 540sec=9min) one attempt take cca 0.5 sec
        - True: device is running
        - False: all attempts have been use device cannot be founded
        """
        attempt = 0
        while attempt <= attempts:
            attempt += 1
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((ip, int(port)))
            if attempt % 20 == 0:
                print("Trying connect to a device {}. Attempts {}/{}".format(device_name, str(attempt), str(attempts)))
            if result == 0:
                sock.close()
                return True
            else:
                sock.close()
                time.sleep(0.5)
                continue
        return False


NetconfAddConfigs().run()
