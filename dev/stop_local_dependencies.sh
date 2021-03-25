#!/bin/bash

echo
echo "----------------------------------------------------------------------"
echo "Stoping docker-compose..."
echo "----------------------------------------------------------------------"
docker-compose -f dev/devdocker/docker-compose.yml stop
docker-compose -f dev/devdocker/docker-compose.yml rm -f
