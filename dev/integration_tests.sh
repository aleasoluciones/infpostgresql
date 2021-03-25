#!/bin/bash

find . -name *pyc* -delete
source "dev/env_develop"

dev/start_local_dependencies.sh
integration_tests
dev/stop_local_dependencies.sh

exit $MAMBA_RETCODE
