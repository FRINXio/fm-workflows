#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
export DIR_PATH="$DIR"
export RUN_CLI_DEVICES_DIR="$DIR_PATH"/scripts/run_cli_devices
export NETCONF_RUN_DIR="$DIR_PATH"/scripts/run_netconf_devices

echo $DIR_PATH
# Set sample topology env variables

export RUN_TESTTOOLS="./scripts/run_cli_devices/run_devices_docker.sh"

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
        *)
            echo -e "${ERROR} Unknow option: ${1}"
            show_help
            exit 1;;
    esac
    shift
  done
}

argumentsCheck "$@"

# -------------- PREPARE NETCONF DEVICES --------------
# Find highest port in generated devices
highest_port=17000
input=$NETCONF_RUN_DIR/testtool_instances.txt
while IFS= read -r line
do
  # devices_array: [0]=schema_name, [1]=device_count, [2]=start_port
  read -ra devices_array <<<"$line"
  port=${devices_array[2]}
  device_count=${devices_array[1]}
  if [ "$port" -gt "$highest_port" ];then
    highest_port=$port
  fi
  if [ "$device_count" -gt 1 ];then
    last_device_port=$((device_count - 1))
    highest_port=$((highest_port + last_device_port))
  fi
done < "$input"

export PORT_RANGE_NETCONF="17000-$highest_port:17000-$highest_port"

# -------------- PREPARE CLI DEVICES --------------
# Find highest port in cli devices
highest_port=10000
input=$RUN_CLI_DEVICES_DIR/cli_devices.txt
while IFS= read -r line
do
  # devices_array: [0]=device name,[1]=port
  read -ra devices_array <<<"$line"
  port=${devices_array[1]}
  if [ "$port" -gt "$highest_port" ];then
    highest_port=$port
  fi
done < "$input"

# Use in docker compose to open ports
export PORT_RANGE="10000-$highest_port:10000-$highest_port"
echo $PORT_RANGE

stackName="fm"
docker service rm "$stackName"_sample-topology
docker stack deploy --compose-file composefiles/swarm-fm-sample-topology.yml $stackName
