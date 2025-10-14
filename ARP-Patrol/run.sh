#!/bin/bash

# Existing startup tasks
/app/service_handler.sh "$@"

# Listen for stdin commands
while read line; do
    echo "Received stdin: $line"
    eval "$line"
done
