#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export DIR_PATH="$DIR"
export RUN_CLI_DEVICES_DIR="$DIR_PATH"/scripts/run_cli_devices
export NETCONF_RUN_DIR="$DIR_PATH"/scripts/run_netconf_devices

echo $DIR_PATH
# Set sample topology env variables

export RUN_TESTTOOLS="./scripts/run_cli_devices/run_devices_docker.sh"
INSTANCES_TO_SIMULATE=""

function show_help() {
cat << EOF
DESCRIPTION:

  USAGE: ./${__SCRIPT_NAME} [OPTIONS]

  Simulate devices.
  Add 'sample-topology', to Frinx Machine swarm stack.
  DEFAULT only cli devices run (to add also netconf devices use parameter -all)
  To run only netconf devices use parameter --only-netconf

  COMMON SETTINGS
    --only-netconf     Run only netconf devices
    --all    Run all CLI and Netconf devices

   Run only specific instances:
   -i65|--iosxr653   Run only iosxr 653 instance. Devices [iosxr653_1, iosxr653_2]
   -i66|--iosxr663   Run only iosxr 663 instance. Devices [iosxr663_1]
   -j|--junos        Run only junos instance. Devices [junos_1]

   -h|--help    Print this help and exit
   -d|--debug   Enable verbose

EOF
}

# ARGUMENT CHECK ------------------------------
function argumentsCheck {

  while [ $# -gt 0 ]
  do
    case "${1}" in
        -h|--help)
            show_help
            exit 0;;

        --only-netconf)
            echo "Starting only Netconf devices"
            export RUN_TESTTOOLS="./scripts/run_netconf_devices/run_netconf_testtool.sh";;
        --all)
            echo "Starting Netconf and CLI devices"
            export RUN_TESTTOOLS="./scripts/run_netconf_devices/run_netconf_testtool.sh & ./scripts/run_cli_devices/run_devices_docker.sh";;
        -i65|--iosxr653)
            INSTANCES_TO_SIMULATE+="IOSXR653,";;
        -i66|--iosxr663)
            INSTANCES_TO_SIMULATE+="IOSXR663,";;
        -j|--junos)
            INSTANCES_TO_SIMULATE+="JUNOS,";;

        *)
            echo -e "${ERROR} Unknow option: ${1}"
            show_help
            exit 1;;
    esac
    shift
  done
}

argumentsCheck "$@"
export INSTANCES_TO_SIMULATE
echo "Starting simulation of these devics: $INSTANCES_TO_SIMULATE"

# Open netconf ports for simulated devices (used in composefile)
export PORT_RANGE_NETCONF="17000-17200:17000-17200"
echo "Opening ports for netconf devices: $PORT_RANGE_NETCONF"

# Open cli ports for simulated devices (used in composefile)
export PORT_RANGE="10000-10015:10000-10015"
echo "Opening ports for cli devices: $PORT_RANGE"

stackName="fm"
docker stack deploy --compose-file ../composefiles/swarm-fm-workflows.yml $stackName
