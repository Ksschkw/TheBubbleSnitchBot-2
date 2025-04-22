#!/bin/bash
set -e

echo "Starting Xvfb..."
Xvfb :99 -screen 0 1280x720x24 &

export DISPLAY=:99
echo "Starting the bot..."
python -u bot.py