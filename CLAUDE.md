# TARS-WIZARD Project Reference

This file tracks project status, architecture decisions, and key information for development.

## Current Status

**Version:** 2.0 (in development)
**Current Phase:** Phase 0 — Repo Setup & Foundations
**Branch:** `phase/0-setup`

## Completed Phases

| Phase | Description | Date | PR |
|-------|-------------|------|----|
| — | Initial codebase (v1.0) | 2025 | — |

## Project Structure

```
TARS-WIZARD/
├── main.py                  # Single entry point (Phase 2)
├── config.yaml              # All settings
├── .env.example             # API key template
├── requirements.txt         # Python dependencies
├── deploy.sh                # Deploy to Pi
├── setup.sh                 # Fresh Pi setup
├── tars/                    # Core package (Phase 1+)
├── software/                # Original code (legacy, being migrated)
│   ├── TARSmaster.py        # Desktop mode with Tkinter GUI
│   └── bundle/              # Headless mode modules
├── hardware/                # 3D printing files and wiring
│   ├── STL/                 # 3D printable parts
│   ├── parts-list.md        # Bill of materials
│   └── wiring-guide.pdf     # Electrical connections
├── docs/                    # Documentation
├── tests/                   # Test suite (Phase 6)
└── .github/                 # CI, issue/PR templates
```

## Architecture Decisions

1. **Single entry point** (`main.py`) replacing both TARSmaster and bundle modes
2. **Rich terminal UI** instead of Tkinter — works over SSH, no X11 needed
3. **GPT-4o-mini** as primary AI model, local LLM (Ollama) as offline fallback
4. **Pi Camera Module v2** with YOLO (local) + GPT-4o-mini vision (cloud)
5. **OpenWakeWord/Porcupine** for "Hey TARS" wake word (not Google STT)
6. **python-dotenv** for API keys — never hardcode in source
7. **config.yaml** for all settings — servo angles, timing, languages, etc.
8. **OpenClaw on DigitalOcean droplet** for remote web tasks

## Key Constraints

- **Servo angles and timing are NOT to be modified** — they are calibrated for real hardware
- **Servo channels:** Torso=0, Left Arm=3, Right Arm=4
- **Movement values:** Forward/Backward=130/-130, Arm Neutral=-28/28
- **Pulse range:** 1000-2000 microseconds at 50Hz PWM

## Development Workflow

```
1. Make changes locally
2. Deploy to Pi: ./deploy.sh
3. Test on hardware: ssh pi@<ip> → python3 main.py
4. Commit and create PR
5. Review and merge to main
```

## Tech Stack

- **Platform:** Raspberry Pi 5 (8GB RAM)
- **Language:** Python 3.10+
- **AI:** GPT-4o-mini + Ollama (offline)
- **Voice:** AWS Polly (TTS) + OpenWakeWord + webrtcvad
- **Hardware:** PCA9685 servo driver, Pi Camera v2
- **UI:** Rich (terminal)
- **Config:** python-dotenv + PyYAML
- **Testing:** pytest + ruff
- **CI:** GitHub Actions
