import unittest
from workers.importDevices import _is_simulated
import os


class IsDeviceSimulated(unittest.TestCase):
    """Test function _is_simulated which filter out non simulated devices from adding them to device inventory"""

    def test_device_type_cli(self):
        """Simulate CLI devices and try to add CLI and NETCONF device to device inventory"""
        os.environ["RUN_TESTTOOLS"] = "./scripts/run_cli_devices/run_devices_docker.sh"
        cli_device_data = {"labels": "CLI", "device_id": "Leaf01"}
        netconf_device_data = {"labels": "NETCONF", "device_id": "IOSXR653_1"}

        self.assertEqual(_is_simulated(cli_device_data), True)
        self.assertEqual(_is_simulated(netconf_device_data), False)

    def test_device_type_netconf(self):
        """Simulate NETCONF device IOSXR653_1 and try to
        add CLI and NETCONF simulated and also non simulated JUNOS device to device inventory"""
        os.environ[
            "RUN_TESTTOOLS"
        ] = "./scripts/run_netconf_devices/run_netconf_testtool.sh"
        os.environ["INSTANCES_TO_SIMULATE"] = "IOSXR653_1"

        cli_device_data = {"labels": "CLI", "device_id": "Leaf01"}
        netconf_device_data = {"labels": "NETCONF", "device_id": "IOSXR653_1"}
        non_simulated_netconf_device_data = {
            "labels": "NETCONF",
            "device_id": "JUNOS_1",
        }

        self.assertEqual(_is_simulated(cli_device_data), False)
        self.assertEqual(_is_simulated(non_simulated_netconf_device_data), False)
        self.assertEqual(_is_simulated(netconf_device_data), True)

    def test_device_type_both(self):
        """Simulate NETCONF device IOSXR653_1 & CLI devices
        try to add CLI and NETCONF device to device inventory"""
        os.environ[
            "RUN_TESTTOOLS"
        ] = "./scripts/run_netconf_devices/run_netconf_testtool.sh & ./scripts/run_cli_devices/run_devices_docker.sh"
        os.environ["INSTANCES_TO_SIMULATE"] = "IOSXR653_1"

        cli_device_data = {"labels": "CLI", "device_id": "Leaf01"}
        netconf_device_data = {"labels": "NETCONF", "device_id": "IOSXR653_1"}

        self.assertEqual(_is_simulated(cli_device_data), True)
        self.assertEqual(_is_simulated(netconf_device_data), True)


if __name__ == "__main__":
    unittest.main()
