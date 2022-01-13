#!/bin/bash

function show_help() {
cat << EOF
DESCRIPTION:

  USAGE: ./${__SCRIPT_NAME} [OPTIONS]
  
  Add fm-workflows services 'demo-workflows' and default 'sample-topology' with CLI devices to FM swarm stack.

  COMMON SETTINGS

   -h|--help    Print this help and exit
   -d|--debug   Enable verbose

   SAMPLE-TOPOLOGY Parameters:
   -ad|--all-devices   Run CLI and netconf devices
   -nd|--only-netconf-devices   Run only netconf devices


EOF
}

sample_topology_parameter=""

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
            sample_topology_parameter+=" --all";;

        -nd|--only-netconf-devices)
            sample_topology_parameter+=" --only-netconf";;

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

# Pull cli-testtool submodule
echo -e "Pulling submodules..."
if [[ ! -d '.git' ]]; then
  git clone https://github.com/FRINXio/yang-schemas.git
else
 git submodule update --init sample-topology/cli-testtool
fi

__SCRIPT_NAME="$(basename "${0}")"
stackName="fm"

INFO='\033[0;96m[INFO]:\033[0;0m'

# Start sample topology and deploy composefile/swarm-fm-workflows.yml (must be deployed from ./start_sample_topology.sh
# because there is exported env variables for composefile
(cd sample-topology && ./start_sample_topology.sh$sample_topology_parameter)

echo -e "${INFO} Startup finished"
echo -e "================================================================================"
echo
echo -e "Use 'docker service ls' to check status of services."
echo -e "Each service has REPLICAS 1/1 when everything works (it may take several minutes to start all services)."
echo
echo -e "Use 'docker stack rm $stackName' to stop all services and"
echo -e "'docker volume prune' to remove old data if needed."
echo
