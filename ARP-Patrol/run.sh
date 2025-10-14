#!/usr/bin/with-contenv bash
# This line is essential for HA environment setup

# The script does not need to run immediately, it needs to wait for service calls.
# We run a stable command to keep the container running indefinitely.

echo "HA-ARP Patrol Service is installed and waiting for service calls."
echo "Interface name is: $(jq --raw-output ".interface" /data/options.json)"

# The standard command to keep a service container running:
tail -f /dev/null
