"""Tests for tars/config.py — config loading and defaults."""

from tars import config


def test_get_existing_key():
    """Config get returns value for existing keys."""
    assert config.get("servo.frequency") == 50


def test_get_nested_key():
    """Config get handles nested dot notation."""
    assert config.get("servo.channels.torso") == 0


def test_get_missing_key_returns_default():
    """Config get returns default for missing keys."""
    assert config.get("nonexistent.key", "fallback") == "fallback"


def test_get_missing_key_returns_none():
    """Config get returns None when no default specified."""
    assert config.get("nonexistent.key") is None


def test_servo_defaults_loaded():
    """Servo config values are loaded correctly."""
    assert config.CHANNEL_TORSO == 0
    assert config.CHANNEL_LEFT_ARM == 3
    assert config.CHANNEL_RIGHT_ARM == 4
    assert config.PULSE_MIN == 1000
    assert config.PULSE_MAX == 2000


def test_voice_defaults_loaded():
    """Voice config values are loaded correctly."""
    assert config.SPEECH_RATE == "-10%"
    assert config.SPEECH_PITCH == "-20Hz"
    assert config.PLAYBACK_SPEED == 1.2


def test_ai_defaults_loaded():
    """AI config values are loaded correctly."""
    assert config.CEREBRAS_MODEL == "llama3.1-8b"
    assert config.AI_MODEL == "gpt-4o-mini"
    assert config.AI_MAX_TOKENS == 30
    assert config.AI_TEMPERATURE == 0.9


def test_personality_defaults():
    """Personality defaults are loaded."""
    assert config.DEFAULT_HUMOR == 50
    assert config.DEFAULT_HONESTY == 50
    assert config.DEFAULT_LANGUAGE == "english"


def test_language_voices_populated():
    """Language voices dict is populated from config."""
    assert "english" in config.LANGUAGE_VOICES
    assert config.LANGUAGE_VOICES["english"] == "en-US-GuyNeural"


def test_movement_messages_populated():
    """Movement messages dict is populated from config."""
    assert "english" in config.MOVEMENT_MESSAGES
    assert "forward" in config.MOVEMENT_MESSAGES["english"]
