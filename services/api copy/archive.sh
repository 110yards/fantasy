#!/bin/bash

usage_tip="usage: archive.sh 'tag'"

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

 gcloud builds submit --config cloudbuild.archive.yaml --substitutions=_TAG="$tag"
