#!/bin/bash

set -e

current_dir=$(pwd)

cd $1

echo "Lint check..."
ruff check . --show-source --format=github
echo "✅"

echo "Format check..."
black . --check

cd $current_dir
