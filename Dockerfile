FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

# System deps
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
    xvfb \
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
    xauth \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    libxi6 \
    libxss1 \
    libgconf-2-4 \
    wget \
    unzip \
    curl \
    gcc \
    g++ \
    make \
    python3-dev \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install Python dependencies first (to benefit from Docker layer caching)
COPY requirements.txt .
RUN pip install -r requirements.txt

# Install Playwright + Chromium browsers
RUN pip install playwright && playwright install --with-deps chromium


# Your code
COPY . .
COPY .env .
# Entrypoint
CMD ["xvfb-run", "python", "bot.py"]