#!/bin/bash

# Read cli_devices.txt and start generated devices with mockdevice.py

echo "STARTING CLI DEVICES"

RUN_CLI_DEVICES_PATH=/./sample-topology/scripts/run_cli_devices
DEVICE_CONFIGS_PATH=/./sample-topology/configs/cli

cd cli-testtool || exit

input=$RUN_CLI_DEVICES_PATH/cli_devices.txt
line_count=0
last_line=$(wc -l < $input)
while IFS= read -r line
do
  # [0]=device name, [1]=port
  read -ra devices_array <<<"$line"
  line_count="$(expr $line_count + 1)"
  device_name=${devices_array[0]}
  port=${devices_array[1]}

  # Check if is last iterate
  if [ "$line_count" != "$last_line" ]; then
    python2.7 mockdevice.py 0.0.0.0 "$port" 1 ssh "$DEVICE_CONFIGS_PATH"/"$device_name".json &
  else
    python2.7 mockdevice.py 0.0.0.0 "$port" 1 ssh "$DEVICE_CONFIGS_PATH"/"$device_name".json
  fi

done < "$input"
