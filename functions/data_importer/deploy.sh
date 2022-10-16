#!/bin/bash

usage_tip="usage: deploy.sh 'target_project'"

usage_tip="$usage_tip\n\n Options:"
usage_tip="$usage_tip\n   target_project\t\t The google cloud project to deploy the image to"
usage_tip="$usage_tip\n\n"

target_project=$1


if [ -z "$target_project" ]; then
    echo "ERROR: target_project must be supplied"
    printf "$usage_tip"
    exit 1
fi

gcloud builds submit --config cloudbuild.yaml --substitutions=_TARGET_PROJECT_ID="$target_project"