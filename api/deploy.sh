#!/bin/bash

usage_tip="usage: deploy.sh 'tag' 'registry' 'target_project' 'endpoint' 'origins'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   tag\t\t\t The container tag to deploy"
usage_tip="$usage_tip\n   registry\t\t The google cloud project registry containing the built image"
usage_tip="$usage_tip\n   registry\t\t The google cloud project to deploy the image to"
usage_tip="$usage_tip\n   endpoint\t\t The HTTP endpoint of the deployed service"
usage_tip="$usage_tip\n   origins\t\t Origins to accept CORS requests from"
usage_tip="$usage_tip\n\n"

tag=$1
registry=$2
target_project=$3
endpoint=$4
origins=$5

if [ -z "$tag" ]; then
    echo "ERROR: tag must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [ -z "$registry" ]; then
    echo "ERROR: registry must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [ -z "$target_project" ]; then
    echo "ERROR: target_project must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [ -z "$endpoint" ]; then
    echo "ERROR: endpoint must be supplied"
    printf "$usage_tip"
    exit 1
fi

if [ -z "$origins" ]; then
    echo "ERROR: origins must be supplied"
    printf "$usage_tip"
    exit 1
fi

gcloud builds submit --config cloudbuild.deploy.yaml --substitutions=_TAG="$tag",_REGISTRY="$registry",_TARGET_PROJECT_ID="$target_project",_ENDPOINT="$endpoint",_ORIGINS="$origins"