#!/bin/bash

scriptName="$(basename "${0}")"
ST_DIR=$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )

SAMPLE_TOPOLOGY_IMAGE_NAME="frinx/sample-topology"
SAMPLE_TOPOLOGY_TAG=${1}

if [ -z "$SAMPLE_TOPOLOGY_TAG" ]
then
      echo "Please insert image tag as argument"
      exit 1;
fi

pushd ${ST_DIR}/.. 

  # Get yang schema git submodule
  echo -e "Pulling submodules..."
  if [[ ! -d '.git' ]]; then
    git clone https://github.com/FRINXio/yang-schemas.git
    git clone https://github.com/FRINXio/cli-testtool.git sample-topology/cli-testtool
  else
    git submodule update --init --recursive
  fi

  echo -e "Copying specific pulled schemas into schema folder..."
  cp -r yang-schemas/cisco-iosxr-653 sample-topology/schemas
  cp -r yang-schemas/cisco-iosxr-663 sample-topology/schemas
  cp -r yang-schemas/junos-16-2021 sample-topology/schemas

  # After all schemas are copied to sample-topology/schemas then build image
  docker build sample-topology/ -t "$SAMPLE_TOPOLOGY_IMAGE_NAME:$SAMPLE_TOPOLOGY_TAG"

popd
