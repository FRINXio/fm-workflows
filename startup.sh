#!/bin/bash

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

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
echo 0:   $workflow_id

while :; do
  while :; do
    curl --silent -H "Content-Type: application/json"  -X GET http://localhost:8080/api/workflow/$workflow_id | json_pp > OUTPUT
    grep -q '^   "status".*:.*"FAILED",' OUTPUT  && break
    grep -q '^   "status".*:.*"COMPLETED",' OUTPUT  && break
  done
  echo Found:
  grep '^   "status"' OUTPUT
  if cat OUTPUT | grep -q '^   "status".*:.*"FAILED",'; then
    echo "waiting 1 minute for netconf-device get started..."
    sleep 60
    echo "execute workflow Write_data_to_netconf_testool..."
    workflow_id=`curl --silent -H "Content-Type: application/json"  -X POST -d "{\"name\":\"Write_data_to_netconf_testool\",\"version\":1,\"input\":{}}" http://localhost:8080/api/workflow/`
    ((c++)) && ((c==3)) && break
    echo $c:   $workflow_id
  else
    echo -e '\nnetconf-testtool configuration OK!\n'
    break
  fi
done

if [[ $c -eq 3 ]]; then
  echo -e '\nnetconf-testtool configuration failed!\n'
fi
