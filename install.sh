#!/bin/bash
set -e

DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )
cd ${DIR}

ERROR='\033[0;31m[ERROR]:\033[0;0m'
WARNING='\033[0;33m[WARNING]:\033[0;0m'
INFO='\033[0;96m[INFO]:\033[0;0m'

echo -e "${INFO} Pulling images"
docker-compose --log-level ERROR -f composefiles/swarm-fm-workflows.yml pull
# Build sample-topology image
cd sample-topology
./install.sh
