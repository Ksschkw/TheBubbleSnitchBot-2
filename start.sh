#!/bin/bash
set -eo pipefail

# Xvfb configuration
XVFB_RES="1280x720x24"
XVFB_ARGS="-screen 0 $XVFB_RES -ac +extension RANDR +extension GLX +render -noreset"

echo "🖥️ Starting Xvfb..."
Xvfb :99 $XVFB_ARGS >/tmp/xvfb.log 2>&1 &
XVFB_PID=$!

# Wait for X server
for i in {1..10}; do
  if xdpyinfo -display :99 >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

# Verify Xvfb
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
  echo "❌ Xvfb failed to start! Logs:"
  cat /tmp/xvfb.log
  exit 1
fi

export DISPLAY=:99

# Critical Chromium flags
CHROMIUM_FLAGS=(
  --no-sandbox
  --disable-dev-shm-usage
  --disable-gpu
  --single-process
  --disable-software-rasterizer
  --disable-setuid-sandbox
  --no-zygote
  --disable-background-networking
)

echo "🤖 Starting bot with Chromium flags..."
exec python -u bot.py "${CHROMIUM_FLAGS[@]}"

# Cleanup
cleanup() {
  kill -TERM $XVFB_PID
}
trap cleanup EXIT