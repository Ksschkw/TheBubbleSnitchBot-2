FROM python:3.11-slim

# Add build arguments for headless environment
ARG DEBIAN_FRONTEND=noninteractive
ARG PLAYWRIGHT_BROWSERS_PATH=/ms-playwright

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=$PLAYWRIGHT_BROWSERS_PATH \
    DISPLAY=:99

# Install system dependencies with precise versioning
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    libegl1 \
    libgles2 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libgtk-3-0 \
    libdrm2 \
    libasound2 \
    libnss3 \
    libatk1.0-0 \
    libatspi2.0-0 \
    libcups2 \
    libxkbcommon0 \
    libxshmfence1 \
    libwayland-client0 \
    libwayland-server0 \
    libharfbuzz0b \
    # Font dependencies
    fonts-liberation fonts-noto-color-emoji \
    # Build essentials
    gcc g++ make python3-dev \
    # Cleanup
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies first for better layer caching
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install playwright

# Install Chromium with all dependencies
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

# Configure entrypoint
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]