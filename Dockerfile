FROM odoo:18

# Reste root tout le long
USER root

# Dépendances système + pip
RUN apt-get update && apt-get install -y \
    python3-pip \
    default-jre-headless \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libxkbcommon0 \
    libpango-1.0-0 \
    libatspi2.0-0 \
    libnss3 \
    libxss1 \
    libgtk-3-0 \
    libdrm2 \
    libxshmfence1 \
    libxext6 \
    libxtst6 \
    ca-certificates \
    fonts-liberation \
    libappindicator3-1 \
    libcurl4 \
    libdbus-glib-1-2 \
    libgdk-pixbuf2.0-0 \
    libglib2.0-0 \
    libnspr4 \
    libu2f-udev \
    wget \
    --no-install-recommends && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python packages
RUN pip3 install --break-system-packages pandas jingtrang playwright

# Install Playwright dependencies and browsers
RUN playwright install --with-deps
USER odoo