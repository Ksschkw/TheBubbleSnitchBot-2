FROM python:3.11-slim

# Essential environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

# Install system dependencies first
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libnss3 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libx11-xcb1 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    fonts-noto-core \
    fonts-freefont-ttf \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages from requirements.txt
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt  # This MUST include python-dotenv

# Install Playwright and Chromium
RUN pip install playwright \
    && playwright install --with-deps chromium

# Copy application files
COPY . .

# Configure entrypoint
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]
