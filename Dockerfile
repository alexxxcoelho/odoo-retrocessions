FROM odoo:18

USER root

# 1. Installer toutes les dépendances système nécessaires
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
    libasound2t64 \
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

# 2. Installer les dépendances Python
RUN pip3 install --break-system-packages pandas jingtrang playwright

# 3. Télécharger les navigateurs Playwright en tant que root
RUN playwright install

# (Optionnel) alias jingtrang
RUN ln -sf /usr/local/bin/jingtrang /usr/local/bin/pyjing

# 4. Revenir à l’utilisateur odoo
USER odoo
