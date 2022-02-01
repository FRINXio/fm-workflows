import unittest
import os
from scripts.run_netconf_devices.generate_devices_setup import GenerateDeviceSetup, INSTANCES_DETAILS, DEVICES_DETAILS, \
    ALL_INSTANCES
from pathlib import Path

GENERATED_NETCONF_DEVICES_FILEPATH = Path("..", "scripts", "run_netconf_devices", "netconf_devices.txt")
GENERATED_TESTTOOL_INSTANCES_FILEPATH = Path("..", "scripts", "run_netconf_devices", "testtool_instances.txt")


def _read_txt_file(file_path: Path) -> list:
    """ Read txt file lines and return each line as element in list"""
    with open(file_path) as f:
        return f.read().splitlines()


class GenerateDevicesSetupNetconf(unittest.TestCase):
    """
        - Check count of generated devices and instances in files
        - Check if in generated files are correct data for devices and also instances
    """
    def test_generate_all_instances_default(self):
        """ Generate files with all netconf devices by default """
        os.environ["INSTANCES_TO_SIMULATE"] = ""
        GenerateDeviceSetup()
        netconf_devices_file_data = _read_txt_file(GENERATED_NETCONF_DEVICES_FILEPATH)
        testtool_instances_file_data = _read_txt_file(GENERATED_TESTTOOL_INSTANCES_FILEPATH)

        device_count = 0
        # Count devices for selected instances
        for instance in ALL_INSTANCES:
            device_count += len(DEVICES_DETAILS[instance])
            self._validate_netconf_devices_file(instance, netconf_devices_file_data)
            self._validate_testtool_instances_file(instance, testtool_instances_file_data)

        self.assertEqual(len(netconf_devices_file_data), device_count)
        self.assertEqual(len(testtool_instances_file_data), len(ALL_INSTANCES))

    def test_generate_all_instances_one_by_one(self):
        """ Generate all netconf instances one by one and validate generated files """
        for instance in ALL_INSTANCES:
            os.environ["INSTANCES_TO_SIMULATE"] = instance
            GenerateDeviceSetup()

            netconf_devices_file_data = _read_txt_file(GENERATED_NETCONF_DEVICES_FILEPATH)
            testtool_instances_file_data = _read_txt_file(GENERATED_TESTTOOL_INSTANCES_FILEPATH)

            self.assertEqual(len(netconf_devices_file_data), len(DEVICES_DETAILS[instance]))
            self.assertEqual(len(testtool_instances_file_data), 1)

            self._validate_netconf_devices_file(instance, netconf_devices_file_data)
            self._validate_testtool_instances_file(instance, testtool_instances_file_data)

    def test_generated_mix_of_instances(self):
        """ Generate mixed selection of instances and validate generated files """
        mixed_lists_of_instances = [["IOSXR653", "IOSXR663"], ["JUNOS", "IOSXR653"], ["JUNOS", "IOSXR663"]]
        for instances_list in mixed_lists_of_instances:
            os.environ["INSTANCES_TO_SIMULATE"] = ",".join(instances_list)
            GenerateDeviceSetup()

            netconf_devices_file_data = _read_txt_file(GENERATED_NETCONF_DEVICES_FILEPATH)
            testtool_instances_file_data = _read_txt_file(GENERATED_TESTTOOL_INSTANCES_FILEPATH)

            device_count = 0
            # Count devices for selected instances
            for instance in instances_list:
                device_count += len(DEVICES_DETAILS[instance])
                self._validate_netconf_devices_file(instance, netconf_devices_file_data)
                self._validate_testtool_instances_file(instance, testtool_instances_file_data)

            self.assertEqual(len(netconf_devices_file_data), device_count)
            self.assertEqual(len(testtool_instances_file_data), len(instances_list))

    def _validate_netconf_devices_file(self, selected_instance: str, netconf_devices_file_data: list) -> None:
        """ Check all devices for selected instance and validate name and port with generated file """
        for device in DEVICES_DETAILS[selected_instance]:
            expected_device_line = f"{device['name']} {device['port']}"
            self.assertIn(expected_device_line, netconf_devices_file_data)

    def _validate_testtool_instances_file(self, selected_instance: str, testtool_instances_file_data: list) -> None:
        """ Check selected instance and validate schema, count_of_devices and starting port with generated file """
        instance = INSTANCES_DETAILS[selected_instance]
        expected_instance_line = f"{instance['schema']} {instance['count_of_devices']} {instance['starting_port']}"
        self.assertIn(expected_instance_line, testtool_instances_file_data)

    def tearDown(self) -> None:
        """ Delete created files for testing netconf_devices.txt & testtool_instances.txt"""
        GENERATED_NETCONF_DEVICES_FILEPATH.unlink()
        GENERATED_TESTTOOL_INSTANCES_FILEPATH.unlink()
