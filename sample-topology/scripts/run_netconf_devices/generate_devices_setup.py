import os

# Key = instance, values = [schema, count_of_device, starting port]
INSTANCES_DETAILS = {"IOSXR653": {"schema": "cisco-iosxr-653", "count_of_devices": 2, "starting_port": 17000},
                     "IOSXR663": {"schema": "cisco-iosxr-663", "count_of_devices": 1, "starting_port": 17100},
                     "JUNOS": {"schema": "junos-16-2021", "count_of_devices": 1, "starting_port": 17200}}

# Key = instance, values = [name, port]
DEVICES_DETAILS = {"IOSXR653": [{"name": "iosxr653_1", "port": 17000}, {"name": "iosxr653_2", "port": 17001}],
                   "IOSXR663": [{"name": "iosxr663_1", "port": 17100}],
                   "JUNOS": [{"name": "junos_1", "port": 17200}]}

ALL_INSTANCES = ["IOSXR653", "IOSXR663", "JUNOS"]


class GenerateDeviceSetup:
    """ Generate testtool_instances.txt & netconf_devices.txt files"""
    TESTTOOL_INSTANCE_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'testtool_instances.txt')
    NETCONF_DEVICES_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'netconf_devices.txt')

    def __init__(self):
        SELECTED_INSTANCES = os.getenv("INSTANCES_TO_SIMULATE")
        # convert str to list ex. "IOSXR653,IOSXR663,JUNOS," -> ["IOSXR653", "IOSXR663", "JUNOS"]
        self.SELECTED_INSTANCES = ALL_INSTANCES if not SELECTED_INSTANCES else list(
            filter(None, SELECTED_INSTANCES.split(",")))
        self.generate_devices()
        self.generate_testtool_instances()

    def generate_devices(self):
        """ Generate netconf_devices.txt with selected devices to simulate"""
        with open(self.NETCONF_DEVICES_PATH, 'w') as file:
            for instance in self.SELECTED_INSTANCES:
                for device in DEVICES_DETAILS[instance]:
                    name, port = device.values()
                    file.write("{} {}\n".format(name, port))

    def generate_testtool_instances(self):
        """ Generate testool_instances.txt with selected instances to simulate"""
        with open(self.TESTTOOL_INSTANCE_PATH, 'w') as file:
            for selected_instance in self.SELECTED_INSTANCES:
                instance = INSTANCES_DETAILS[selected_instance]
                file.write("{} {} {}\n".format(instance["schema"], instance["count_of_devices"],instance["starting_port"]))


if __name__ == "__main__":
    GenerateDeviceSetup()
