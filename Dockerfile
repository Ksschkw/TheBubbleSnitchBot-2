FROM python:3.11-slim

# Essential environment variables
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DISPLAY=:99 \
    TZ=UTC \
    LANG=en_US.UTF-8 \
    LANGUAGE=en_US:en \
    LC_ALL=en_US.UTF-8

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    x11vnc \
    xauth \
    xfonts-100dpi \
    xfonts-75dpi \
    xfonts-scalable \
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
    fonts-noto-core \
    fonts-noto-extra \
    fonts-noto-color-emoji \
    fonts-freefont-ttf \
    gcc \
    g++ \
    make \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \
    && localedef -i en_US -c -f UTF-8 -A /usr/share/locale/locale.alias en_US.UTF-8

# Install Python dependencies
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install playwright==1.42.0

# Install Chromium with dependencies
RUN playwright install --with-deps chromium

# Copy application files
COPY . .

# Configure entrypoint
COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh

ENTRYPOINT ["/app/start.sh"]