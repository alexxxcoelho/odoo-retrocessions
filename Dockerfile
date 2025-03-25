FROM odoo:18

USER root

RUN apt-get update && apt-get install -y \
    python3-pip \
    default-jre-headless \
    ca-certificates \
    libcurl4 \
    wget \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages utilisés réellement
RUN pip3 install --break-system-packages pandas jingtrang

USER odoo
