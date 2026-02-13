# Bundle Mode (Modular Deployment)

Lightweight, headless scripts designed for running TARS on a Raspberry Pi without a monitor or GUI. Each module handles one responsibility and can be run independently or together.

**Best for:** Deploying TARS as a standalone robot running off battery power.

## Prerequisites

- Completed [Raspberry Pi Setup](raspberry-pi-setup.md)
- Configured [API Keys](api-keys.md) (in `bundle/voice.py`)
- PCA9685 servo driver wired and detected

## The Bundle Files

```
software/bundle/
├── mechanism.py      # Servo control (movement functions)
├── voice.py          # Voice assistant (listen + respond + move)
├── controller.py     # Gamepad/keyboard input → servo commands
└── run_master.py     # Launches voice + controller together
```

## Quick Start — Run Everything

```bash
cd ~/TARS-WIZARD/software/bundle
python3 run_master.py
```

This starts two threads:
- **Voice thread** — Listens for speech commands and responds
- **Controller thread** — Reads gamepad input for manual control

Both threads can control the servos simultaneously.

## Running Individual Modules

### Voice only (no controller)
```bash
python3 voice.py
```
TARS listens for voice commands, talks back, and controls servos.

### Controller only (no voice)
```bash
python3 controller.py
```
Control TARS with your gamepad or keyboard. No AI, no speech — pure manual control.

### Mechanism only (test servos)
```bash
python3 -c "import mechanism; mechanism.move_forward()"
```
Test individual movements without voice or controller.

## Module Details

### mechanism.py
The servo driver. Provides movement functions:
- `move_forward()` — Walking gait (torso + arm sequence)
- `turn_left()` — Left turn
- `turn_right()` — Right turn
- `neutral()` — Return to neutral position

All functions accept an optional `language` parameter for localized feedback messages.

On import, the module initializes the PCA9685 and sets servos to neutral.

### voice.py
The AI voice assistant. Handles:
- Speech recognition (Google Speech Recognition via microphone)
- AI responses (OpenAI GPT-3.5 with TARS personality)
- Text-to-speech (AWS Polly with voice modification)
- Movement commands (calls mechanism.py functions)
- Weather and time queries
- Multi-language support

### controller.py
Gamepad/keyboard input handler. Maps keys to movements:

| Key | Action |
|-----|--------|
| W / Up Arrow | Move forward |
| A / Left Arrow | Turn left |
| D / Right Arrow | Turn right |
| Q | Quit |

**Important:** You may need to change the `device_path` at the top of the file. See [Controller Setup](controller-setup.md) for finding your device's event path.

### run_master.py
Simple launcher that starts voice and controller in parallel threads.

## Running on Boot

To have TARS start automatically when the Pi powers on:

### Using systemd

Create a service file:

```bash
sudo nano /etc/systemd/system/tars.service
```

Add:
```ini
[Unit]
Description=TARS Robot
After=network.target

[Service]
ExecStart=/usr/bin/python3 /home/pi/TARS-WIZARD/software/bundle/run_master.py
WorkingDirectory=/home/pi/TARS-WIZARD/software/bundle
User=pi
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl enable tars.service
sudo systemctl start tars.service
```

Check status:
```bash
sudo systemctl status tars.service
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `ModuleNotFoundError: mechanism` | Make sure you're running from inside the `bundle/` directory |
| Controller not responding | Check device path — see [Controller Setup](controller-setup.md) |
| Voice timeout errors | Check microphone: `arecord -l`. Ensure USB mic is plugged in |
| Servos jitter on startup | Normal — they're finding neutral position. Check power supply if excessive |

## Next Steps

- [Controller Setup](controller-setup.md) — Find and configure your gamepad
- [TARSmaster Mode](tarsmaster-mode.md) — Full desktop experience with GUI
