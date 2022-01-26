#!/bin/bash

echo "Deleting fm_sample-topology & fm_demo-workflows services"
docker service rm fm_sample-topology fm_demo-workflows