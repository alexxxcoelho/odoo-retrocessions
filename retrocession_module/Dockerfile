FROM odoo:18

USER root
RUN apt-get update && apt-get install -y python3-pip default-jre-headless && \
    echo 'export _JAVA_OPTIONS="-XX:CompressedClassSpaceSize=256m"' > /etc/profile.d/java_opts.sh && \
    pip3 install --break-system-packages pandas && \
    pip3 install --break-system-packages --no-cache-dir jingtrang && \
    pip3 install --break-system-packages playwright && \
    playwright install-deps && \
    playwright install && \
    ln -sf /usr/local/bin/jingtrang /usr/local/bin/pyjing && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

USER odoo