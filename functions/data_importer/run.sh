#!/bin/bash

if [ -f .env ]; then
  echo "Configuring environment"
  export $(echo $(cat .env | sed 's/#.*//g'| xargs) | envsubst)
fi

echo "Starting background function"
functions-framework --target=data_importer