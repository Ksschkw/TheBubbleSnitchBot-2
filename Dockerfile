FROM python:3.11-slim

# Add Vulkan and updated dependencies
ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PLAYWRIGHT_BROWSERS_PATH=/ms-playwright \
    VK_ICD_FILENAMES=/usr/share/vulkan/icd.d/intel_icd.x86_64.json

RUN apt-get update && apt-get install -y --no-install-recommends \
    xvfb \
    xauth \
    libgl1-mesa-glx \
    libgl1-mesa-dri \
    vulkan-tools \
    mesa-vulkan-drivers \
    libvulkan1 \
    libxcb-randr0 \
    libxcb-xfixes0 \
    libxshmfence1 \
    libwayland-client0 \
    libwayland-server0 \
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
    fonts-noto-core \
    fonts-freefont-ttf \
    gcc g++ make python3-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install -r requirements.txt \
    && pip install playwright==1.42.0

RUN playwright install --with-deps chromium

COPY . .

COPY start.sh /app/start.sh
RUN chmod +x /app/start.sh
ENTRYPOINT ["/app/start.sh"]