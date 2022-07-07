#!/usr/bin/env bash

cd "$(dirname "${BASH_SOURCE[0]}")" || exit

WORKERS_TAG="try"

docker build --tag "frinx/demo-workflows:$WORKERS_TAG" "."
docker service update --force "fm_demo-workflows" --image "frinx/demo-workflows:$WORKERS_TAG"
