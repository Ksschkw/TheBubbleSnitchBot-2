#!/bin/bash
set -e

# Configure Xvfb with modern display settings
SCREEN_RES="1280x720x24"
XVFB_ARGS="-screen 0 ${SCREEN_RES} -ac +extension RANDR +extension GLX -nolisten tcp"

echo "Starting Xvfb with options: ${XVFB_ARGS}"
Xvfb :99 $XVFB_ARGS &
XVFB_PID=$!

# Wait for X server to initialize
sleep 2

# Verify Xvfb is actually running
if ! xdpyinfo -display :99 >/dev/null 2>&1; then
  echo "❌ Xvfb failed to start! Diagnostic info:"
  glxinfo -display :99 2>&1 || true
  exit 1
fi

export DISPLAY=:99

# Critical Chromium flags for container environments
CHROMIUM_FLAGS="--no-sandbox --disable-dev-shm-usage --disable-gpu --single-process"

echo "Starting bot with Chromium flags: ${CHROMIUM_FLAGS}"
exec python -u bot.py $CHROMIUM_FLAGS

# Cleanup on exit
kill $XVFB_PID