# TARSmaster Mode

The all-in-one desktop experience. TARSmaster launches a Tkinter GUI terminal, voice assistant, and controller listener in a single process.

**Best for:** Desktop/laptop connected to your Pi via SSH with X11 forwarding, or running directly on the Pi with a monitor attached.

## Prerequisites

- Completed [Raspberry Pi Setup](raspberry-pi-setup.md)
- Configured [API Keys](api-keys.md)
- PCA9685 servo driver wired and detected (`sudo i2cdetect -y 1` shows `0x40`)

## Running TARSmaster

```bash
cd ~/TARS-WIZARD/software
python3 TARSmaster.py
```

This opens the TARS Terminal Interface — a green-on-black console window.

## What It Does

TARSmaster runs three systems simultaneously:

1. **GUI Console** — Type commands directly into the terminal input
2. **Voice Listener** — Continuously listens through the microphone for voice commands
3. **Controller Poller** — Reads gamepad/controller input if one is connected

All three feed into the same command processor, so you can interact with TARS through any input method.

## Available Commands

### Voice/Text Commands

| Command | What TARS Does |
|---------|---------------|
| `move forward` or `take 2 steps` | Walks forward (torso + arm sequence) |
| `turn left` | Turns left |
| `turn right` | Turns right |
| `time` or `date` | Tells you the current time (sarcastically) |
| `weather` | Reports the weather for your configured city |
| `speak [language]` | Switches to another language (spanish, french, german, italian, portuguese, japanese) |
| `stop` or `exit` | Shuts down TARS |
| Anything else | Gets a sarcastic AI response from TARS |

### Controller Buttons

| Button | Action |
|--------|--------|
| A | Move forward |
| B | Turn right |
| X | Turn left |
| Y | Neutral position |
| Start | Shut down |

## Features

### Multi-language Support
Say "speak french" and TARS switches everything — AI responses, movement feedback, and voice synthesis — to French. Supported languages:
- English, Spanish, French, German, Italian, Portuguese, Japanese

### Personality Settings
TARS has adjustable humor and honesty levels (0-100%), just like in the movie. These affect how the AI generates responses. Default is 50% for both.

### Software-Only Mode
If servo hardware isn't connected, TARSmaster automatically falls back to software-only mode. The AI conversation and voice features still work — servo commands just get logged to the console instead of moving physical servos.

## Running Over SSH

If your Pi is headless (no monitor), you can still use TARSmaster with X11 forwarding:

```bash
ssh -X pi@tars.local
cd ~/TARS-WIZARD/software
python3 TARSmaster.py
```

The GUI window will appear on your local machine.

> **Note:** For a lighter-weight headless option without GUI, use [Bundle Mode](bundle-mode.md) instead.

## Troubleshooting

| Issue | Fix |
|-------|-----|
| `_tkinter.TclError: no display` | You need X11 forwarding (`ssh -X`) or a connected monitor |
| Voice not working | Check mic with `arecord -l`. Make sure API keys are set |
| Controller not detected | See [Controller Setup](controller-setup.md) for finding the right event path |
| Servos don't move | Check I2C: `sudo i2cdetect -y 1`. Check wiring and power supply |

## Next Steps

- [Bundle Mode](bundle-mode.md) — Lighter-weight headless alternative
- [Controller Setup](controller-setup.md) — Configure your gamepad
