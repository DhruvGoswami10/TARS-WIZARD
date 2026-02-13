# TARS Software

The code that brings TARS to life. Two deployment modes depending on your setup.

## Modes

### TARSmaster (Desktop)

```bash
python3 TARSmaster.py
```

All-in-one experience with a Tkinter GUI terminal. Runs voice assistant, controller polling, and servo control in a single process. Best when you have a monitor connected or are using SSH with X11 forwarding.

[Full guide →](../docs/tarsmaster-mode.md)

### Bundle (Headless Pi)

```bash
cd bundle
python3 run_master.py
```

Lightweight modular scripts without GUI. Designed for standalone Raspberry Pi deployments running off battery power. Run all modules together or individually.

[Full guide →](../docs/bundle-mode.md)

## Quick Setup

### 1. Install dependencies
```bash
sudo apt install -y python3-pip python3-dev python3-smbus i2c-tools libasound-dev portaudio19-dev ffmpeg

pip3 install --break-system-packages \
  evdev adafruit-circuitpython-pca9685 \
  adafruit-circuitpython-busdevice adafruit-blinka \
  speechrecognition openai boto3 requests pydub
```

### 2. Add your API keys
Edit `TARSmaster.py` or `bundle/voice.py` and replace the placeholder values:

```python
openai.api_key = 'YOUR OPENAI API KEY HERE'
ACCESS_KEY = 'YOUR AWS ACCESS KEY HERE'
SECRET_KEY = 'YOUR AWS SECRET KEY HERE'
```

See [API Keys Guide](../docs/api-keys.md) for detailed instructions.

### 3. Run
```bash
python3 TARSmaster.py        # Desktop mode
# or
cd bundle && python3 run_master.py  # Headless mode
```

## File Structure

```
software/
├── TARSmaster.py          # All-in-one desktop mode with GUI
├── README.md              # You are here
└── bundle/
    ├── mechanism.py       # Servo control (PCA9685)
    ├── voice.py           # Voice assistant (speech + AI + TTS)
    ├── controller.py      # Gamepad/keyboard input
    └── run_master.py      # Launches voice + controller together
```

## Voice Commands

| Command | Action |
|---------|--------|
| "move forward" / "take 2 steps" | Walk forward |
| "turn left" | Turn left |
| "turn right" | Turn right |
| "time" / "date" | Current time |
| "weather" | Weather report |
| "speak [language]" | Switch language |
| "stop" / "exit" | Shut down |
| Anything else | Sarcastic AI response |

## Supported Languages

English, Spanish, French, German, Italian, Portuguese, Japanese
