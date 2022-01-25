
testool_instances.txt and netconf_devices.txt MUST HAVE EMPTY LINE AT THE END OF FILE

To customize list of simulated devices or instances need modify constants INSTANCES_DETAILS & DEVICES_DETAILS generate_device_setup.py

Process:
- Run netconf testtool instances (every running instance can have maximum 100 devices and only one schema can run on instance)
- Push netconf config and operation data to running simulated devices

netconf_devices:
iosxr653_1 17000
iosxr653_2 17001
iosxr663_1 17100
junos_1 17200

testtool_instances:
cisco-iosxr-653 2 17000
cisco-iosxr-663 1 17100
junos-16-2021 1 17200
