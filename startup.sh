export CONSTRAINT_HOSTNAME=$(hostname)
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