#!/bin/bash


expected=`cat .python-version`
actual=`python --version`

if grep -q "$expected" <<< "$actual"; then
    exit 0
else
    echo "Environment is not using expected python version.  Expected '$expected', found '$actual'."
    exit 1
fi