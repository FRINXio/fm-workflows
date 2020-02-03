#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

function copy_workers {
  docker cp workers/. micros:/home/app/netinfra_utils/workers
}

curl_workers_copy=(curl --silent --write-out 'HTTPSTATUS:%{http_code}' -X GET 'http://127.0.0.1:8080/api/metadata/taskdefs/UNIFIED_check_unified_node_exists')

function check_container {
local cmd=$1[@]

for i in {100..1}; do

  response=$(${!cmd})
  echo -ne "Waiting for $1 to respond. For $i seconds\033[0K\r"

  HTTP_STATUS=$(echo $response | tr -d '\n' | sed -e 's/.*HTTPSTATUS://')
  if [ $HTTP_STATUS -eq 200 ];
  then
    echo
    echo "Microservices is ready"
    return 0
  fi
  sleep 1
done

echo
echo "Microservices not healthy"
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

check_container curl_workers_copy

# Imports workflows
import_workflows

# Import devices
import_devices

echo -e '\nDemo workers/workflows/devices successfully imported!\n'