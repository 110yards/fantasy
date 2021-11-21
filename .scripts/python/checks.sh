#!/bin/bash

set -e
scripts/python/python-version.sh
scripts/python/lint.sh ./api
scripts/python/test.sh ./api