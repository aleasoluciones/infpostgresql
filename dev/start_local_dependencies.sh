#!/bin/bash

find . -name *pyc* -delete
source "dev/env_develop"

echo
echo "----------------------------------------------------------------------"
echo "Starting docker-compose..."
echo "----------------------------------------------------------------------"
docker-compose -f dev/infpostgresql_devdocker/docker-compose.yml up -d

# Wait for ports to be available
TIMEOUT=30
printf "Checking port ${POSTGRES_PORT} ... "
if [[ $(uname) == 'Linux' ]]; then
    timeout ${TIMEOUT} bash -c "until echo > /dev/tcp/localhost/${POSTGRES_PORT}; do sleep 0.5; done" > /dev/null 2>&1
    [[ $? -eq 0 ]] && echo -e '\e[32mOK\e[0m' || echo -e '\e[31mNOK\e[0m'
elif [[ -x $(command -v nc) ]]; then
    timeout ${TIMEOUT} bash -c "until nc -vz ${POSTGRES_HOSTNAME} ${POSTGRES_PORT}; do sleep 0.5; done" > /dev/null 2>&1
    [[ $? -eq 0 ]] && echo -e '\e[32mOK\e[0m' || echo -e '\e[31mNOK\e[0m'
else
    echo -e "Unable to check port ${POSTGRES_PORT}. Just sleeping for 5 seconds ..."
    sleep 5
fi
