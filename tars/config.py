import os
from pathlib import Path

import yaml
from dotenv import load_dotenv

# Find project root (directory containing config.yaml)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent

# Load .env file if it exists
_env_path = _PROJECT_ROOT / ".env"
if _env_path.exists():
    load_dotenv(_env_path)

# Load config.yaml
_config_path = _PROJECT_ROOT / "config.yaml"
with open(_config_path, encoding="utf-8") as f:
    _config = yaml.safe_load(f)


def get(key_path, default=None):
    """Get a config value using dot notation: get('servo.channels.torso')"""
    keys = key_path.split(".")
    value = _config
    for key in keys:
        if isinstance(value, dict) and key in value:
            value = value[key]
        else:
            return default
    return value


def env(key, default=None):
    """Get an environment variable (from .env or system)."""
    return os.environ.get(key, default)


# ─── Convenience accessors ──────────────────────────────────

# API Keys
OPENAI_API_KEY = env("OPENAI_API_KEY", "")
WEATHER_API_KEY = env("WEATHER_API_KEY", "")
CITY_NAME = env("CITY_NAME", "")

# Servo
SERVO_FREQUENCY = get("servo.frequency", 50)
CHANNEL_TORSO = get("servo.channels.torso", 0)
CHANNEL_LEFT_ARM = get("servo.channels.left_arm", 3)
CHANNEL_RIGHT_ARM = get("servo.channels.right_arm", 4)

FORWARD_POS = get("servo.positions.forward", 130)
NEUTRAL_POS = get("servo.positions.neutral", 0)
BACKWARD_POS = get("servo.positions.backward", -130)
LEFT_ARM_NEUTRAL_POS = get("servo.positions.left_arm_neutral", -28)
RIGHT_ARM_NEUTRAL_POS = get("servo.positions.right_arm_neutral", 28)

PULSE_MIN = get("servo.pulse.min", 1000)
PULSE_MAX = get("servo.pulse.max", 2000)

# Movement timing
STEP_DELAY = get("movement.step_delay", 0.2)
ARM_DELAY = get("movement.arm_delay", 0.3)

# Voice
LISTEN_TIMEOUT = get("voice.listen_timeout", 3)
SPEECH_RATE = get("voice.speech_rate", "-10%")
SPEECH_PITCH = get("voice.speech_pitch", "-20Hz")
PLAYBACK_SPEED = get("voice.playback_speed", 1.2)
LOW_PASS_FILTER = get("voice.low_pass_filter", 3000)
HIGH_PASS_FILTER = get("voice.high_pass_filter", 300)
VOLUME_REDUCTION = get("voice.volume_reduction", 3)
VOLUME_BOOST = get("voice.volume_boost", 8)

# AI
AI_MODEL = get("ai.model", "gpt-4o-mini")
AI_MAX_TOKENS = get("ai.max_tokens", 50)
AI_TEMPERATURE = get("ai.temperature", 0.9)

# Personality
DEFAULT_HUMOR = get("personality.humor", 50)
DEFAULT_HONESTY = get("personality.honesty", 50)
DEFAULT_LANGUAGE = get("personality.default_language", "english")

# Weather
WEATHER_API_URL = get("weather.api_url", "https://api.openweathermap.org/data/2.5/weather")
WEATHER_UNITS = get("weather.units", "metric")

# Languages — build lookup dicts from config
_languages = get("languages", {})
LANGUAGE_VOICES = {lang: info["voice_id"] for lang, info in _languages.items()}
MOVEMENT_MESSAGES = {
    lang: info.get("movement_messages", {}) for lang, info in _languages.items()
}
