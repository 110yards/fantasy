#!/bin/bash

usage_tip="usage: deploy.sh 'tag' 'env'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   tag\t\t\t The container tag to deploy"
usage_tip="$usage_tip\n   env\t\t The environment to deploy to (dev, test, live)"
usage_tip="$usage_tip\n\n"

tag=$1
env=$2

if [ -z "$tag" ]; then
    echo "ERROR: tag must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [ -z "$env" ]; then
    echo "ERROR: env must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [[ ! "dev test live" =~ $env ]]; then
    echo "ERROR: env must be one of dev, test, live (was '$env')"
    printf "$usage_tip"
    exit 1
fi

gcloud builds submit --config cloudbuild.deploy.yaml --substitutions=_TAG="$tag",_ENVIRONMENT="$env"
