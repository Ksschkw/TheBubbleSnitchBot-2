#!/bin/bash
set -eo pipefail

# Configure GPU environment
export MESA_GL_VERSION_OVERRIDE=4.5
export MESA_GLSL_VERSION_OVERRIDE=450
export LD_LIBRARY_PATH=/usr/lib/x86_64-linux-gnu:/usr/lib64:$LD_LIBRARY_PATH

# Start Xvfb with Vulkan support
echo "🖥️ Starting Xvfb with Vulkan..."
Xvfb :99 -screen 0 1280x720x24 +extension GLX +extension RANDR +extension RENDER -ac -nolisten tcp -maxclients 2048 &
XVFB_PID=$!

# Wait for X server
for i in {1..10}; do
  if xdpyinfo -display :99 >/dev/null 2>&1; then
    break
  fi
  sleep 0.5
done

export DISPLAY=:99

# Launch bot with critical flags
echo "🤖 Starting bot with hardened Chromium config..."
exec python -u bot.py