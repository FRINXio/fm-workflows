#!/bin/bash

function show_help() {
cat << EOF
DESCRIPTION:

  USAGE: ./${__SCRIPT_NAME} [OPTIONS]
  
  Add fm-workflows services 'demo-workflows' and default 'sample-topology' with CLI devices to FM swarm stack.

  COMMON SETTINGS

   -h|--help    Print this help and exit
   -d|--debug   Enable verbose

   -ci|--clean-inventory    Clean device inventory

   SAMPLE-TOPOLOGY Parameters:
   -ad|--all-devices   Run CLI and netconf devices
   -nd|--only-netconf-devices   Run only netconf devices

   Run only specific netconf instance (use with parameter -ad or -nd):
   -i65|--iosxr653   Run only iosxr 653 instance. Devices [iosxr653_1, iosxr653_2]
   -i66|--iosxr663   Run only iosxr 663 instance. Devices [iosxr663_1]
   -j|--junos        Run only junos instance. Devices [junos_1]

EOF
}

export RUN_TESTTOOLS="./scripts/run_cli_devices/run_devices_docker.sh"
INSTANCES_TO_SIMULATE=""

function argumentsCheck {
    while [ $# -gt 0 ]
    do
    case "${1}" in
        -h|--help) 
            show_help
            exit 0;;

        -d|--debug) 
            set -x;;
        -ad|--all-devices)
            echo "Starting Netconf and CLI devices"
            export RUN_TESTTOOLS="./scripts/run_netconf_devices/run_netconf_testtool.sh & ./scripts/run_cli_devices/run_devices_docker.sh";;
        -nd|--only-netconf-devices)
            echo "Starting only Netconf devices"
            export RUN_TESTTOOLS="./scripts/run_netconf_devices/run_netconf_testtool.sh";;
        -i65|--iosxr653)
            INSTANCES_TO_SIMULATE+="IOSXR653,";;
        -i66|--iosxr663)
            INSTANCES_TO_SIMULATE+="IOSXR663,";;
        -j|--junos)
            INSTANCES_TO_SIMULATE+="JUNOS,";;
        -ci|--clean-inventory)
            docker exec -it "$(docker ps -qf "name=fm_inventory-postgres")" psql -U postgres -a inventory -c 'delete from device_inventory;'
            echo "Device inventory has been cleaned.";;
        *)
            echo "Unknow option: ${1}"
            show_help
            exit 1;;
    esac
    shift
    done
}

function setManagerIpAddrEnv {
  MANAGER_IP_ADDR=$(hostname -I | cut -d ' ' -f 1)
  export MANAGER_IP_ADDR
}

argumentsCheck "$@"
setManagerIpAddrEnv

# =======================================
# Program starts here
# =======================================

__SCRIPT_NAME="$(basename "${0}")"
stackName="fm"

export INSTANCES_TO_SIMULATE
echo "Simulating these devices: $INSTANCES_TO_SIMULATE"

# Open netconf ports for simulated devices (used in composefile)
export PORT_RANGE_NETCONF="17000-17200:17000-17200"
echo "Opening ports for netconf devices: $PORT_RANGE_NETCONF"

# Open cli ports for simulated devices (used in composefile)
export PORT_RANGE="10000-10015:10000-10015"
echo "Opening ports for cli devices: $PORT_RANGE"

stackName="fm"
docker stack deploy --compose-file composefiles/swarm-fm-workflows.yml $stackName


INFO='\033[0;96m[INFO]:\033[0;0m'

echo -e "${INFO} Startup finished"
echo -e "================================================================================"
echo
echo -e "Use 'docker service ls' to check status of services."
echo -e "Each service has REPLICAS 1/1 when everything works (it may take several minutes to start all services)."
echo
echo -e "Use 'docker stack rm $stackName' to stop all services and"
echo -e "'docker volume prune' to remove old data if needed."
echo
