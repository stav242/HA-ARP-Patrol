#!/bin/bash
# The Add-on reads service call arguments from standard input (stdin)

set -e

# Read the JSON payload sent by Home Assistant
INPUT_JSON=$(</dev/stdin)

# Use jq to parse the required fields from the JSON input
TARGET_IP=$(echo "$INPUT_JSON" | jq -r '.target_ip')
TARGET_MAC=$(echo "$INPUT_JSON" | jq -r '.target_mac')
GATEWAY_IP=$(echo "$INPUT_JSON" | jq -r '.gateway_ip')
GATEWAY_MAC=$(echo "$INPUT_JSON" | jq -r '.gateway_mac')
DURATION=$(echo "$INPUT_JSON" | jq -r '.duration_seconds')

# Get the interface from the add-on configuration options
INTERFACE=$(jq --raw-output ".interface" /data/options.json)

# --- Input Validation ---
if [ -z "$TARGET_IP" ] || [ -z "$TARGET_MAC" ] || [ -z "$GATEWAY_IP" ] || [ -z "$GATEWAY_MAC" ] || [ -z "$DURATION" ]; then
    echo "[FATAL] Missing one or more required service parameters from automation data."
    echo "Received JSON: $INPUT_JSON"
    exit 1
fi

echo "[INFO] Starting ARP Blocker Service on $INTERFACE..."
echo "[INFO] Target: $TARGET_IP, Duration: $DURATION seconds."

# --- Execute the Python Script ---
# Pass the arguments to the Python script
python3 /app/arp_dos_service.py \
    "$TARGET_IP" \
    "$TARGET_MAC" \
    "$GATEWAY_IP" \
    "$GATEWAY_MAC" \
    "$DURATION" \
    "$INTERFACE"

