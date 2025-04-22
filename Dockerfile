FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    xvfb          \   
    # X virtual framebuffer
    xauth         \   
    # for xvfb-run’s auth
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxi6 \
    libxss1 \
    libgconf-2-4 \
    wget unzip curl \
    gcc g++ make python3-dev \  
    # for any native Python extensions
 && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
 && pip install -r requirements.txt


RUN pip install playwright \
 && playwright install --with-deps chromium

COPY . .

ENV PORT=10000
EXPOSE 10000

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
ENTRYPOINT ["/app/start.sh"]