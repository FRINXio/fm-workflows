#!/bin/bash

echo "STARTING NETCONF DEVICES"
netconf_testtool_file=$(find /./netconf-testtool/ | grep netconf-testtool-)

# Generate testtool_instances.txt & netconf_devices.txt
python2.7 /./sample-topology/scripts/run_netconf_devices/generate_devices_setup.py

# RUN DEVICES WITH NETCONF TESTTOOL
input=/./sample-topology/scripts/run_netconf_devices/testtool_instances.txt
line_count=0
last_line=$(wc -l < $input)

python2.7 /./sample-topology/scripts/run_netconf_devices/netconf_add_configs.py &

# Start netconf testtool count of devices for each schema
while IFS= read -r line
do
  # devices_array: [0]=schema name, [1]=count of devices, [2]=starting port. ex. [0]=cisco-iosxr-653, [1]=2, [2]=17000
  read -ra devices_array <<<"$line"
  line_count="$(expr $line_count + 1)"

  if [ "$line_count" != "$last_line" ]; then
    java -jar $netconf_testtool_file --schemas-dir /./sample-topology/schemas/"${devices_array[0]}" --md-sal true --device-count "${devices_array[1]}" --starting-port "${devices_array[2]}" &
  else
    java -jar $netconf_testtool_file --schemas-dir /./sample-topology/schemas/"${devices_array[0]}" --md-sal true --device-count "${devices_array[1]}" --starting-port "${devices_array[2]}"
  fi

done < "$input"

