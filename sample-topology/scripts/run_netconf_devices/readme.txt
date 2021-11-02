
testool_instances.txt and netconf_devices.txt MUST HAVE EMPTY LINE AT THE END OF FILE!
 (dont forget to add extra empty line at end of file if you changing device selection)

- Add netconf devices to run into netconf_devices.txt in format "<name> <port>" ex. (isoxr 17000)
- Add number of netconf instances (1 instance = 1 schema) into testtool_instances.txt
    in format "<schema_name> <count_of_instances> <port_begin>" (every instance must have port start increased by 100)
     ex. "cisco-iosxr-653 2 17000
          cisco-iosxr-663 1 17100
          junos-16-2021 1 17200"

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
