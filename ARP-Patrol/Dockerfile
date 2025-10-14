# Start from the standard Home Assistant base image for Python apps
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies (jq is needed for run.sh)
RUN apk add --no-cache tcpdump build-base python3 py3-pip jq

# Copy your Python script into the container
COPY arp_dos_service.py /app/

# Install Python packages (Scapy)
# FIX: Use --break-system-packages to bypass the PEP 668 error
RUN pip3 install scapy --break-system-packages

# Make the Python script executable
RUN chmod a+x /app/arp_dos_service.py

# No ENTRYPOINT or CMD here, relying on config.json and external service calls
