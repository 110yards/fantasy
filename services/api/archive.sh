#!/bin/bash

usage_tip="usage: archive.sh 'tag' 'registry'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   tag\t\t The container tag to deploy"
usage_tip="$usage_tip\n   registry\t The google cloud project registry to push the built image to"
usage_tip="$usage_tip\n\n"

tag=$1
if [ -z "$tag" ]; then
    echo "ERROR: tag must be supplied"
    printf "$usage_tip"
    exit 1
fi

registry=$2
if [ -z "$registry" ]; then
    echo "ERROR: registry must be supplied"
    printf "$usage_tip"
    exit 1
fi


 gcloud builds submit --config cloudbuild.archive.yaml --substitutions=_TAG="$tag",_REGISTRY="$registry"