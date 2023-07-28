#!/bin/bash

set -e


usage_tip="usage: .scripts/python/checks.sh 'service_path'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   service_path\t\t\t The path to the cloud run service"
usage_tip="$usage_tip\n\n"

service_path=$1

if [ -z "$service_path" ]; then
    echo "ERROR: service_path must be supplied"
    printf "$usage_tip"
    exit 1
fi

.scripts/python/python-version.sh
.scripts/python/lint.sh $service_path
.scripts/python/test.sh $service_path
