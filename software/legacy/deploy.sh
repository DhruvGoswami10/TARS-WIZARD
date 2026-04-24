#!/bin/bash
# TARS-WIZARD Deploy Script
# Syncs code from your laptop to the Raspberry Pi via SSH.
#
# Usage:
#   ./deploy.sh                  # Sync code to Pi
#   ./deploy.sh --run            # Sync code and start TARS
#   ./deploy.sh --dry-run        # Show what would be synced (no changes)
#
# First-time setup:
#   1. Edit the PI_USER and PI_HOST variables below
#   2. Set up SSH key auth: ssh-copy-id pi@<your-pi-ip>
#   3. Make executable: chmod +x deploy.sh

# ─── Configuration ──────────────────────────────────────────
PI_USER="pi"
PI_HOST="raspberrypi.local"     # Change to your Pi's IP or hostname
PI_DIR="~/TARS-WIZARD"
# ─────────────────────────────────────────────────────────────

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [[ "$1" == "--dry-run" ]]; then
    echo -e "${YELLOW}[DRY RUN] Showing what would be synced...${NC}"
    rsync -avzn --delete \
        --exclude '.env' \
        --exclude '__pycache__' \
        --exclude '.git' \
        --exclude 'venv' \
        --exclude '*.pyc' \
        --exclude '.DS_Store' \
        --exclude 'node_modules' \
        "$SCRIPT_DIR/" "${PI_USER}@${PI_HOST}:${PI_DIR}/"
    exit 0
fi

echo -e "${GREEN}[DEPLOY] Syncing TARS-WIZARD to ${PI_USER}@${PI_HOST}...${NC}"

rsync -avz --delete \
    --exclude '.env' \
    --exclude '__pycache__' \
    --exclude '.git' \
    --exclude 'venv' \
    --exclude '*.pyc' \
    --exclude '.DS_Store' \
    --exclude 'node_modules' \
    "$SCRIPT_DIR/" "${PI_USER}@${PI_HOST}:${PI_DIR}/"

echo -e "${GREEN}[DEPLOY] Sync complete.${NC}"

if [[ "$1" == "--run" ]]; then
    echo -e "${GREEN}[DEPLOY] Starting TARS on Pi...${NC}"
    ssh "${PI_USER}@${PI_HOST}" "cd ${PI_DIR} && source venv/bin/activate && python3 main.py"
fi
