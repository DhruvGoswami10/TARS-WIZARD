#!/bin/bash
# TARS-WIZARD — One-command startup for Raspberry Pi
# Usage: ./start.sh [options]
#   ./start.sh              # Normal mode (text + voice)
#   ./start.sh --text-only  # Text only (no mic/speaker)
#   ./start.sh --wake-word  # Enable wake word detection
#
# To auto-start on boot, add to crontab:
#   crontab -e
#   @reboot /home/pi/TARS-WIZARD/start.sh

set -e

# Navigate to project directory
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

# Activate virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
elif [ -d ".venv" ]; then
    source .venv/bin/activate
else
    echo "No virtual environment found. Run setup.sh first."
    exit 1
fi

# Launch TARS
echo "Starting TARS-WIZARD..."
python main.py "$@"
