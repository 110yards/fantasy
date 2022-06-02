#!/bin/bash

set -e

usage_tip="usage: deploy.sh 'service_path'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   service_path\t\t\t The path to the cloud run service"
usage_tip="$usage_tip\n\n"

service_path=$1

if [ -z "$service_path" ]; then
    echo "ERROR: service_path must be supplied"
    printf "$usage_tip"
    exit 1
fi

rm -rf .tmp/
mkdir .tmp

cp .dockerignore .tmp
cp -r .scripts .tmp
cp -a $service_path/. .tmp
cp -r yards_py .tmp/yards_py
cp setup.py .tmp/yards_py

cd .tmp

./archive.sh "${@:2}"
./deploy.sh "${@:2}"
