#!/bin/bash

current_dir=$(pwd)
cd $1

pytest tests/ --disable-warnings

cd $current_dir
