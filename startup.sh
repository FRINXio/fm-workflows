
function show_help() {
cat << EOF
DESCRIPTION:

  USAGE: ./${__SCRIPT_NAME} [OPTIONS]
  
  Add fm-workflows services 'sample-topology', 'demo-workflows' to Frinx Machine swarm stack.

  OPTIONS

    -u|--uniconfig-service      
          Define Uniconfig Servicename (multi-node deployment)

  COMMON SETTINGS

    -h|--help     Print help

EOF
}

function argumentsCheck {
    while [ $# -gt 0 ]
    do
    case "${1}" in
        -h|--help) show_help
            exit 0;;
        
        -u|--uniconfig-service)
            if [[ ${2} != "-"* ]] && [[ ! -z ${2} ]]  ; then
                UNICONFIG_SERVICENAME="${2}"; shift
            fi;;

        -d|--debug) 
            set -x;;

        *) 
            echo "Unknow option: ${1}"
            show_help
            exit 1;;
    esac
    shift
    done
}

# =======================================
# Program starts here
# =======================================

__SCRIPT_NAME="$(basename "${0}")"
stackName="fm"
UNICONFIG_SERVICENAME="uniconfig"


argumentsCheck "$@"
export UNICONFIG_SERVICENAME


INFO='\033[0;96m[INFO]:\033[0;0m'
echo -e "${INFO} Uniconfig service name: $UNICONFIG_SERVICENAME"
docker stack deploy --compose-file composefiles/swarm-fm-workflows.yml $stackName


echo -e "${INFO} Startup finished"
echo -e "================================================================================"
echo
echo -e "Use 'docker service ls' to check status of services."
echo -e "Each service has REPLICAS 1/1 when everything works (it may take several minutes to start all services)."
echo
echo -e "Use 'docker stack rm $stackName' to stop all services and"
echo -e "'docker volume prune' to remove old data if needed."
echo