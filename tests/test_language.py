"""Tests for tars/commands/language.py — language state and voice mapping."""

from tars.commands.language import LanguageState, get_movement_message, get_supported_languages, get_voice_id


def test_language_state_defaults():
    """LanguageState has correct defaults."""
    state = LanguageState()
    assert state.current_language == "english"
    assert state.humor == 0.5
    assert state.honesty == 0.5


def test_get_voice_id_english():
    """English voice ID is correct."""
    assert get_voice_id("english") == "en-US-GuyNeural"


def test_get_voice_id_spanish():
    """Spanish voice ID is correct."""
    assert get_voice_id("spanish") == "es-ES-AlvaroNeural"


def test_get_voice_id_unknown_returns_default():
    """Unknown language falls back to Matthew."""
    result = get_voice_id("klingon")
    assert result == "Matthew"


def test_get_supported_languages():
    """Supported languages list is populated."""
    langs = get_supported_languages()
    assert "english" in langs
    assert "spanish" in langs
    assert len(langs) >= 7


def test_get_movement_message_english():
    """English movement messages work."""
    assert get_movement_message("forward", "english") == "Moving forward"
    assert get_movement_message("left", "english") == "Turning left"


def test_get_movement_message_unknown_language():
    """Unknown language falls back to english."""
    result = get_movement_message("forward", "klingon")
    assert result == "Moving forward"


def test_get_movement_message_unknown_type():
    """Unknown movement type returns 'Moving'."""
    result = get_movement_message("backflip", "english")
    assert result == "Moving"
