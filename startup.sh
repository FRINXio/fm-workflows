#!/bin/bash

#Install sample-topology------------------------

set -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

input_containers=("sample-topology")

cd ${DIR}

echo 'Pull images'
docker-compose -f docker-compose.bridge.yml pull "${input_containers[@]}"

# Clean up
docker system prune -f

#Startup sample-topology------------------------

# Common functions
script="startup.sh"

function start_bridge_container {
  docker-compose -f docker-compose.bridge.yml up -d "$1"
}

function start_host_container {
  docker-compose -f docker-compose.host.yml up -d "$1"
}

# Loop arguments

while [ "$1" != "" ];
do
case $1 in
    -n | --networking)
    networking="$2"
    shift
    shift
    ;;
    *)    # unknown option
    echo "$script: illegal option $1"
    exit 1 #error
    ;;
esac
done

# Clean up docker
docker system prune -f

# Starts containers
if [ "$networking" = "host" ]; then
    start_host_container "sample-topology"
    echo -e 'Startup sample-topology finished!\n'
    # Restart container to allow add the record for "sample-topology" to /etc/host table
    docker stop "uniconfig"
    docker rm "uniconfig"
    echo -e 'Stopping uniconfig finished!\n'
    start_host_container "uniconfig"
    echo -e 'Startup uniconfig finished!\n'
elif [ -z "$networking" ]; then
    start_bridge_container "sample-topology"
    echo -e 'Startup sample-topology finished!\n'
else
    echo "Only host is allowed"
    exit
fi

#Startup workflows------------------------

function copy_workers {
  docker cp workers/. micros:/home/app/netinfra_utils/workers
}

function wait_for_worker_registrations {
for i in {100..1}; do

  response=$(curl --silent --write-out 'HTTPSTATUS:%{http_code}' -X GET 'http://127.0.0.1:8080/api/metadata/taskdefs/UNIFIED_check_unified_node_exists')
  echo "Waiting for workers to be registered."

  HTTP_STATUS=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
  if [ $HTTP_STATUS -eq 200 ];
  then
    echo "Workers have been registered."
    return 0
  fi
  sleep 1
done

echo "Workers failed to register."
return 1

}

function import_workflows {
  docker cp workflows/. micros:/home/app/netinfra_utils/workflows
  docker cp importWorkflow.sh micros:/home/app/netinfra_utils/
  docker exec micros bash -c "./importWorkflow.sh"
}

function import_devices {
  docker cp devices/. micros:/home/app/netinfra_utils/devices
  docker cp importDevices.py micros:/home/app/netinfra_utils/
  docker exec micros bash -c "python importDevices.py devices/cli_device_data.csv devices/cli_device_import.json"
  docker exec micros bash -c "  python importDevices.py devices/netconf_device_data.csv devices/netconf_device_import.json"
}

# Copy workers into running container
copy_workers

# Restart micros to register workers
docker container restart micros

# Wait for new worker to register
wait_for_worker_registrations

# Imports workflows
import_workflows

# Import devices
import_devices

echo -e '\nDemo workers/workflows/devices successfully imported!\n'

#Write config to netconf-testtool
echo "waiting 1 minute for netconf-device get started..."
sleep 60
echo "execute workflow Write_data_to_netconf_testool..."
workflow_id=`curl --silent -H "Content-Type: application/json"  -X POST -d "{\"name\":\"Write_data_to_netconf_testool\",\"version\":1,\"input\":{}}" http://localhost:8080/api/workflow/`
# counter c - we try to execute workflow max 3 times untill success
c=1
echo $c:   $workflow_id

while :; do
  while :; do
    curl --silent -H "Content-Type: application/json"  -X GET http://localhost:8080/api/workflow/$workflow_id | json_pp > OUTPUT
    grep -q '^   "status".*:.*"FAILED",' OUTPUT  && break
    grep -q '^   "status".*:.*"COMPLETED",' OUTPUT  && break
  done
  echo Found:
  grep '^   "status"' OUTPUT
  if cat OUTPUT | grep -q '^   "status".*:.*"FAILED",'; then
    ((c++)) && ((c==4)) && break
    echo "execute workflow Write_data_to_netconf_testool..."
    workflow_id=`curl --silent -H "Content-Type: application/json"  -X POST -d "{\"name\":\"Write_data_to_netconf_testool\",\"version\":1,\"input\":{}}" http://localhost:8080/api/workflow/`
    echo $c:   $workflow_id
  else
    echo -e '\nnetconf-testtool configuration OK!\n'
    break
  fi
done

if [[ $c -eq 4 ]]; then
  echo -e '\nnetconf-testtool configuration failed!\n'
fi

rm OUTPUT
