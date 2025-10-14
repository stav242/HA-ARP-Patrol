#!/bin/bash
# This script is executed when Home Assistant calls the service via addon_stdin

# Read the JSON payload sent by Home Assistant
INPUT_JSON=$(</dev/stdin)

# Use jq to parse the required fields from the JSON input
# Note: jq is needed because HA sends data as a JSON blob.
TARGET_IP=$(echo "$INPUT_JSON" | jq -r '.target_ip')
TARGET_MAC=$(echo "$INPUT_JSON" | jq -r '.target_mac')
GATEWAY_IP=$(echo "$INPUT_JSON" | jq -r '.gateway_ip')
GATEWAY_MAC=$(echo "$INPUT_JSON" | jq -r '.gateway_mac')
DURATION=$(echo "$INPUT_JSON" | jq -r '.duration_seconds')

# Get the interface from the add-on config options (saved during setup)
INTERFACE=$(jq --raw-output ".interface" /data/options.json)

# --- Execute the Python Script ---
/usr/bin/python3 /app/arp_patrol.py \
    "$TARGET_IP" "$TARGET_MAC" "$GATEWAY_IP" "$GATEWAY_MAC" "$DURATION" "$INTERFACE"

# Crucial: Exit cleanly so the HA service manager knows the task is done.
exit 0
