# TARS WIZARD

**Build your own TARS robot from the movie Interstellar.**

![TARS](media/TARS-1.gif)

TARS WIZARD is a complete, open-source guide to building a walking, talking replica of the TARS robot from Christopher Nolan's *Interstellar*. Everything you need is here — 3D print files, wiring diagrams, software, parts list, and step-by-step guides.

[![Website](https://img.shields.io/badge/Website-TARS%20WIZARD-blue)](https://tars-wizard.vercel.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-support-orange)](https://www.buymeacoffee.com/DhruvG24)

---

## What You'll Build

A fully functional TARS replica that can:

- **Walk** — Servo-driven walking gait with torso and arm movement
- **Talk** — AI-powered voice assistant with the sarcastic TARS personality (via OpenAI)
- **Listen** — Speech recognition for voice commands
- **Speak** — Text-to-speech with a modified robotic voice (via AWS Polly)
- **Be controlled** — Gamepad/controller support for manual movement
- **Speak multiple languages** — English, Spanish, French, German, Italian, Portuguese, Japanese

## What's In This Repo

```
TARS-WIZARD/
│
├── hardware/              3D print files, wiring guide, parts list
│   ├── STL/               All printable parts
│   ├── wiring-guide.pdf   PCA9685, servo, and power connections
│   └── parts-list.md      Full shopping list with links
│
├── software/              Code that runs on the Raspberry Pi
│   ├── TARSmaster.py      All-in-one desktop mode (GUI + voice + controller)
│   └── bundle/            Headless mode for standalone Pi deployments
│       ├── mechanism.py   Servo control
│       ├── voice.py       Voice assistant
│       ├── controller.py  Gamepad input
│       └── run_master.py  Launches everything
│
├── docs/                  Step-by-step guides
│   ├── raspberry-pi-setup.md
│   ├── api-keys.md
│   ├── tarsmaster-mode.md
│   ├── bundle-mode.md
│   └── controller-setup.md
│
└── media/                 GIFs and images
```

## Parts List (Quick View)

| Component | Purpose |
|-----------|---------|
| Raspberry Pi 5 | The brain |
| 3x LD-3015MG Metal Gear Servos | Torso + arms |
| PCA9685 Servo Driver | Controls servos via I2C |
| 12V to 5V DC-DC Converter | Power regulation |
| LiPo Battery 11.1V | Servo power |
| Powerbank | Pi power |
| 5" LCD Display | Status screen |
| Mini USB Microphone | Voice input |
| Bluetooth Speaker | Voice output |
| 8BitDo Controller | Manual control |
| 3D Printed Parts | The body |

**[Full parts list with purchase links →](hardware/parts-list.md)**

**Estimated cost: ~$200-280** (excluding 3D printer)

## Getting Started

### 1. Print the parts
Download the STL files from [`hardware/STL/`](hardware/STL/) and print them. PLA or PETG, 0.2mm layer height, 20-30% infill.

### 2. Buy the components
Everything is listed in the [parts list](hardware/parts-list.md) with direct purchase links.

### 3. Wire it up
Follow the [wiring guide](hardware/wiring-guide.pdf) to connect servos, PCA9685, power, and peripherals.

### 4. Set up the Raspberry Pi
Flash the OS and install dependencies — full walkthrough in the [Pi setup guide](docs/raspberry-pi-setup.md).

### 5. Get your API keys
You'll need OpenAI and AWS Polly credentials. The [API keys guide](docs/api-keys.md) walks you through it.

### 6. Run TARS

**Desktop mode** (with GUI):
```bash
cd software
python3 TARSmaster.py
```

**Headless mode** (standalone Pi):
```bash
cd software/bundle
python3 run_master.py
```

## Guides

| Guide | Description |
|-------|-------------|
| [Raspberry Pi Setup](docs/raspberry-pi-setup.md) | Flash OS, install dependencies, enable I2C |
| [API Keys](docs/api-keys.md) | Get OpenAI, AWS Polly, and weather API credentials |
| [TARSmaster Mode](docs/tarsmaster-mode.md) | All-in-one desktop experience with GUI terminal |
| [Bundle Mode](docs/bundle-mode.md) | Lightweight headless scripts for standalone Pi |
| [Controller Setup](docs/controller-setup.md) | Pair your gamepad and find the device path |

## How It Works

TARS runs on a **Raspberry Pi 5** with three **LD-3015MG servos** controlled through a **PCA9685 servo driver** over I2C. The walking gait coordinates torso rotation with arm swings.

The voice system uses **Google Speech Recognition** to capture commands, **OpenAI GPT-3.5** to generate responses with TARS's signature sarcasm, and **AWS Polly** for text-to-speech — modified with speed and filter adjustments to sound more robotic.

A **gamepad controller** (8BitDo recommended) connects via Bluetooth for manual movement control.

## Project Deep Dive

For a practical software roadmap (what to fix first, OpenClaw-lite direction, autonomy path, and enterprise considerations), see [docs/repo-deep-dive.md](docs/repo-deep-dive.md).

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you'd like to change.

## Support the Project

If TARS WIZARD helped you build something cool, consider buying me a coffee:

[![Buy Me A Coffee](https://img.shields.io/badge/Buy%20Me%20A%20Coffee-☕-orange?style=for-the-badge)](https://www.buymeacoffee.com/DhruvG24)

## License

[MIT](LICENSE) — Use it, modify it, build your own TARS, share it with the world.

---

*"Everybody good? Plenty of slaves for my robot colony?"* — TARS
