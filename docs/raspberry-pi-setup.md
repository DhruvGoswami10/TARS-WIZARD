# Raspberry Pi Setup for TARS

This guide walks you through flashing the OS, installing dependencies, and prepping your Pi for TARS.

## What You Need

- Raspberry Pi 5 (4GB or 8GB)
- MicroSD card (32GB+ recommended)
- USB keyboard/mouse (for initial setup)
- Monitor + Micro HDMI to HDMI cable
- Internet connection (Wi-Fi or Ethernet)

## Step 1: Flash Raspberry Pi OS

1. Download [Raspberry Pi Imager](https://www.raspberrypi.com/software/) on your computer
2. Insert your microSD card
3. Open Raspberry Pi Imager and select:
   - **Device:** Raspberry Pi 5
   - **OS:** Raspberry Pi OS (64-bit) — the full desktop version
   - **Storage:** Your microSD card
4. Click the gear icon to pre-configure:
   - Set hostname (e.g., `tars`)
   - Enable SSH
   - Set username and password
   - Configure Wi-Fi (SSID and password)
   - Set locale/timezone
5. Click **Write** and wait for it to finish
6. Insert the microSD into your Pi and power it on

## Step 2: Initial Pi Configuration

Once booted, open a terminal and run:

```bash
sudo apt update && sudo apt upgrade -y
```

### Enable I2C (required for servo driver)

```bash
sudo raspi-config
```

Navigate to: **Interface Options → I2C → Enable**

Reboot after enabling:
```bash
sudo reboot
```

### Verify I2C is working

After reboot, check that the PCA9685 servo driver is detected:

```bash
sudo apt install -y i2c-tools
sudo i2cdetect -y 1
```

You should see address `0x40` in the grid — that's your PCA9685.

## Step 3: Install System Dependencies

```bash
sudo apt install -y \
  python3-pip \
  python3-dev \
  python3-smbus \
  i2c-tools \
  libasound-dev \
  portaudio19-dev \
  ffmpeg
```

## Step 4: Install Python Packages

```bash
pip3 install --break-system-packages \
  evdev \
  adafruit-circuitpython-pca9685 \
  adafruit-circuitpython-busdevice \
  adafruit-blinka \
  speechrecognition \
  openai \
  boto3 \
  requests \
  pydub
```

> **Note:** The `--break-system-packages` flag is needed on newer Raspberry Pi OS versions that use externally managed Python environments. This is safe for our use case.

## Step 5: Clone the Repository

```bash
cd ~
git clone https://github.com/DhruvGoswami10/TARS-WIZARD.git
cd TARS-WIZARD/software
```

## Step 6: Set Up API Keys

Before running TARS, you need to configure your API keys. See the [API Keys Guide](api-keys.md) for detailed instructions.

Edit the Python files and replace the placeholder values:
- `YOUR OPENAI API KEY HERE`
- `YOUR AWS ACCESS KEY HERE`
- `YOUR AWS SECRET KEY HERE`
- `WEATHER API KEY HERE`
- `YOUR CITY NAME HERE`

## Step 7: Test the Setup

### Test servo control
```bash
cd ~/TARS-WIZARD/software/bundle
python3 -c "import mechanism; mechanism.neutral()"
```

If your servos move to neutral position, hardware is working.

### Test voice (requires API keys)
```bash
python3 voice.py
```

Speak a command — if TARS responds, you're good to go.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `i2cdetect` shows nothing | Check wiring — SDA to GPIO 2, SCL to GPIO 3. Make sure I2C is enabled |
| `ModuleNotFoundError: adafruit_pca9685` | Re-run the pip install command above |
| `ALSA errors` when using microphone | Run `arecord -l` to check if mic is detected. Try a different USB port |
| `Permission denied` on `/dev/input/event*` | Run with `sudo` or add user to `input` group: `sudo usermod -aG input $USER` |
| Servos jitter or don't move | Check power supply — servos need stable 5-6V. The 12V to 5V converter handles this |

## Next Steps

- [Set up your API keys](api-keys.md)
- [Run TARSmaster Mode](tarsmaster-mode.md) (desktop with GUI)
- [Run Bundle Mode](bundle-mode.md) (headless Pi)
- [Configure your controller](controller-setup.md)
