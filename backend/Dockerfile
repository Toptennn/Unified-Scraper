# 1. Base image
FROM python:3.11-slim

# 2. Install system dependencies for Chrome and Selenium
RUN apt-get update && apt-get install -y \
    curl \
    gnupg \
    unzip \
    wget \
    xvfb \
    dbus-x11 \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub | gpg --dearmor -o /usr/share/keyrings/googlechrome-linux-keyring.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/googlechrome-linux-keyring.gpg] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# 3. Set workdir
WORKDIR /app

# 4. Copy dependencies & install Python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy app code
COPY . .

# 6. Create directories for scraper outputs and cookies
RUN mkdir -p /app/output /app/cookies

# 7. Set environment variables for Chrome and Display
ENV CHROME_BIN=/usr/bin/google-chrome \
    CHROME_PATH=/usr/bin/google-chrome \
    CHROMIUM_PATH=/usr/bin/google-chrome \
    GOOGLE_CHROME_BIN=/usr/bin/google-chrome \
    DISPLAY=:99 \
    DBUS_SESSION_BUS_ADDRESS=/dev/null

# 8. Create startup script for Chrome stability
RUN echo '#!/bin/bash\n\
# Start virtual display\n\
Xvfb :99 -ac -screen 0 1280x1024x16 &\n\
# Start dbus\n\
dbus-daemon --system --fork\n\
# Start the application\n\
exec "$@"' > /start.sh && chmod +x /start.sh

# 9. Expose port
EXPOSE 8000

# 10. Run FastAPI via Uvicorn with startup script
CMD ["/start.sh", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
