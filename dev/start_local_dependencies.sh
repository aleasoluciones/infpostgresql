#!/bin/bash

find . -name *pyc* -delete
source "dev/env_develop"

echo
echo "----------------------------------------------------------------------"
echo "Starting docker-compose..."
echo "----------------------------------------------------------------------"
docker-compose -f dev/devdocker/docker-compose.yml up -d

# Wait for ports to be available
TIMEOUT=30
printf "Checking port ${LOCAL_DB_PORT} ... "
if [[ $(uname) == 'Linux' ]]; then
    timeout ${TIMEOUT} bash -c "until echo > /dev/tcp/localhost/${LOCAL_DB_PORT}; do sleep 0.5; done" > /dev/null 2>&1
    [[ $? -eq 0 ]] && echo -e '\e[1;32mOK\e[0m' || echo -e '\e[1;31mNOK\e[0m'
elif [[ -x $(command -v nc) ]]; then
    timeout ${TIMEOUT} bash -c "until nc -vz ${DOCKER_HOST_IP} ${LOCAL_DB_PORT}; do sleep 0.5; done" > /dev/null 2>&1
    [[ $? -eq 0 ]] && echo -e '\e[1;32mOK\e[0m' || echo -e '\e[1;31mNOK\e[0m'
else
    echo -e "Unable to check port ${LOCAL_DB_PORT}. Just sleeping for 5 seconds ..."
    sleep 5
fi
