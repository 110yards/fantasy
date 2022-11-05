#!/bin/bash

set -e

runNumber=$1
ref=$2

if [ -z "$runNumber" ]; then
    echo "Run number is required"
    echo "Usage:"
    echo "  version.sh <run_number>"
    exit 1
fi

echo "On branch $ref"

dateVer="$(date +'%Y.%m.%d')"
version=""

if [ "$ref" == "main" ]; then
    echo "Versioning for production"
    version="$dateVer.$runNumber"
else
    echo "Versioning for test"
    version="test.$runNumber"
fi

echo "version = $version"
echo "version=$version" >> $GITHUB_ENV