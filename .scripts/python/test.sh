#!/bin/bash

pytest $1 --disable-warnings
ret=$?

if [ "$ret" = 5 ]; then
    echo "No tests collected."
    exit 0
fi

exit "$ret"