# Start from the standard Home Assistant base image for Python apps
ARG BUILD_FROM
FROM ${BUILD_FROM}

# Set the working directory inside the container
WORKDIR /app

# Install system dependencies
RUN apk add --no-cache tcpdump build-base python3 py3-pip jq

# Copy your Python script into the container
COPY arp_patrol.py /app/ <--- Script name updated here

# Install Python packages (Scapy)
RUN pip3 install scapy --break-system-packages

# Copy and setup run.sh
COPY run.sh /
RUN chmod a+x /run.sh

# Set the entry point
ENTRYPOINT ["/run.sh"]
