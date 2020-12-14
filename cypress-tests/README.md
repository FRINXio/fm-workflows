# List of tests with some remarks.

Basically by tests are covered [the use cases][2] described in [Frinx documentation][1].

## 00kibana_fm_init_spec.js
This is to remove introductory page in next tests related to inventory (kibana). 

## 01mount_device_spec.js
Here are mounted two devices directly via FRINX UniConfig. No need to have a device definition in repository.

## 02mount_all_devices_spec.js
[Mount all cli devices in inventory][3], workflow *Mount_all_cli_from_inventory* is used.

## 03unmount_incompat_devs_spec.js
See note designated [Important][4]. 

## Loopback use case
[Creating loopback address and retrieving journals of devices][4]  
10create_loopback_spec.js  
12check_loopback.spec.js uses workflow *Read_journal_cli_device* to check loopback at two chosen devices.

### Loopback use case - demonstrate creating of workflow in Workflow designer
11create_wrkfl_check_lpbck_spec.js  uses newly created workflow *Read_journal_cli_device_TEST* to check journal at one chosen device.

## 20lacp_spec.js
[Creating a link aggregation between two nodes][5], uses workflow  *Link_aggregation*

## LLDP use case
30lldp_build_spec.js uses workflow *Build_read_store_LLDP_topology*  
31lldp_kibana_check_spec.js - you can check in inventory (kibana) using index lldp  
32lldp_export_spec.js see [Exporting the IETF topology information in graphviz format][7], uses workflow *Export_LLDP_topology*  
33lldp_graphviz_spec.js uses [visualization tool][8] to display topology

## Obtain data from devices
[Collects platform information from the device and store in the inventory][9]  
40obtain_data_spec.js uses workflow *Read_components_all_from_unified_update_inventory*  
41obtain_data_kibana_check_spec.js - you can check in inventory (kibana) using index inventory-devices 

## Pre-prepare CLI command and re-use it 
[Save a command to inventory and execute saved command on mounted devices][A]  
50commands_save_spec.js uses workflow *Add_cli_show_command_to_inventory*  
51commands_kibana_check_spec.js - you can check in inventory (kibana) using index inventory-show_cmd  
52commands_execute_spec.js uses workflow *Execute_and_read_rpc_cli_device_from_inventory*
53commands_execute_spec.js uses workflow *Execute_and_read_rpc_cli_device_from_inventory_update_inventory*
54commands_execute_kibana_check_spec.js - you can check in inventory (kibana) using index inventory-show_cmd  
55commands_execute_spec.js uses workflow *Execute_all_from_cli_update_inventory*
56commands_execute_kibana_check_spec.js - you can check in inventory (kibana) using index inventory-show_cmd  

## Add device to inventory
60add_device_spec.js  
61add_device_kibana_check_spec.js  
63mount_device_spec.js  
64unmount_device_spec.js  
65add_device_kibana_delete_spec.js  

## Unmount all devices
90unmount_all_devices_spec.js

[1]: https://docs.frinx.io/
[2]: https://docs.frinx.io/FRINX_Machine/use-cases/index.html
[3]: https://docs.frinx.io/FRINX_Machine/use-cases/mount-all-devices-in-inventory/mount-all-devices-in-inventory.html
[4]: https://docs.frinx.io/FRINX_Machine/use-cases/create-loopback-and-read-journal/create-loopback-and-read-journal.html
[5]: https://docs.frinx.io/FRINX_Machine/use-cases/lacp/lacp.html
[6]: https://docs.frinx.io/FRINX_Machine/use-cases/lldp-topology/lldp-topology.html
[7]: https://docs.frinx.io/FRINX_Machine/use-cases/lldp-topology/lldp-topology.html#exporting-the-ietf-topology-information-in-graphviz-format
[8]: https://dreampuf.github.io/GraphvizOnline
[9]: https://docs.frinx.io/FRINX_Machine/use-cases/obtain-platform-inventory-data/obtain-platform-inventory-data.html
[A]: https://docs.frinx.io/FRINX_Machine/use-cases/save-and-run-command/save-and-run-command.html
