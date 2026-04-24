#!/bin/bash
# TARS-WIZARD Raspberry Pi Setup Script
# Run this on a fresh Raspberry Pi to install everything.
#
# Usage (on the Pi):
#   curl -sSL https://raw.githubusercontent.com/DhruvGoswami10/TARS-WIZARD/main/setup.sh | bash
#
# Or if you've already cloned the repo:
#   cd TARS-WIZARD && chmod +x setup.sh && ./setup.sh

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}"
echo "╔══════════════════════════════════════════╗"
echo "║         TARS-WIZARD Setup Script         ║"
echo "║     Building your own TARS from scratch  ║"
echo "╚══════════════════════════════════════════╝"
echo -e "${NC}"

# ─── Step 1: System Update ──────────────────────────────────
echo -e "${GREEN}[1/7] Updating system packages...${NC}"
sudo apt-get update -y
sudo apt-get upgrade -y

# ─── Step 2: System Dependencies ────────────────────────────
echo -e "${GREEN}[2/7] Installing system dependencies...${NC}"
sudo apt-get install -y \
    python3 \
    python3-pip \
    python3-venv \
    git \
    ffmpeg \
    portaudio19-dev \
    libasound-dev \
    libatlas-base-dev \
    i2c-tools \
    python3-smbus

# ─── Step 3: Enable I2C ────────────────────────────────────
echo -e "${GREEN}[3/7] Enabling I2C interface...${NC}"
if ! grep -q "^dtparam=i2c_arm=on" /boot/firmware/config.txt 2>/dev/null && \
   ! grep -q "^dtparam=i2c_arm=on" /boot/config.txt 2>/dev/null; then
    # Try the new path first (Bookworm+), fall back to old path
    if [ -f /boot/firmware/config.txt ]; then
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    else
        echo "dtparam=i2c_arm=on" | sudo tee -a /boot/config.txt
    fi
    echo -e "${YELLOW}  I2C enabled. A reboot will be needed after setup.${NC}"
else
    echo "  I2C already enabled."
fi

# Load I2C module now
sudo modprobe i2c-dev 2>/dev/null || true

# ─── Step 4: Clone Repo (if not already in it) ─────────────
echo -e "${GREEN}[4/7] Setting up TARS-WIZARD repository...${NC}"
if [ ! -f "main.py" ] && [ ! -f "software/TARSmaster.py" ]; then
    if [ -d "$HOME/TARS-WIZARD" ]; then
        echo "  Repository already exists at ~/TARS-WIZARD"
        cd "$HOME/TARS-WIZARD"
    else
        git clone https://github.com/DhruvGoswami10/TARS-WIZARD.git "$HOME/TARS-WIZARD"
        cd "$HOME/TARS-WIZARD"
    fi
else
    echo "  Already in TARS-WIZARD directory."
fi

# ─── Step 5: Python Virtual Environment ────────────────────
echo -e "${GREEN}[5/7] Creating Python virtual environment...${NC}"
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

# ─── Step 6: Python Dependencies ───────────────────────────
echo -e "${GREEN}[6/7] Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r requirements.txt

# Install Pi-specific packages
pip install adafruit-circuitpython-pca9685 adafruit-blinka evdev picamera2 2>/dev/null || \
    echo -e "${YELLOW}  Some Pi-specific packages failed (normal on non-Pi systems).${NC}"

# ─── Step 7: Environment File ──────────────────────────────
echo -e "${GREEN}[7/7] Setting up environment...${NC}"
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo -e "${YELLOW}  Created .env from template. You need to add your API keys.${NC}"
    echo -e "${YELLOW}  Edit with: nano .env${NC}"
else
    echo "  .env already exists."
fi

# ─── Verify ─────────────────────────────────────────────────
echo ""
echo -e "${BLUE}╔══════════════════════════════════════════╗"
echo "║           Setup Complete!                ║"
echo "╚══════════════════════════════════════════╝${NC}"
echo ""
echo -e "${GREEN}Next steps:${NC}"
echo "  1. Add your API keys:  nano .env"
echo "  2. Verify I2C devices: i2cdetect -y 1"
echo "  3. Start TARS:         source venv/bin/activate && python3 main.py"
echo ""

# Check if reboot needed for I2C
if ! ls /dev/i2c-* 1>/dev/null 2>&1; then
    echo -e "${YELLOW}Note: I2C was just enabled. Please reboot before running TARS:${NC}"
    echo "  sudo reboot"
fi
