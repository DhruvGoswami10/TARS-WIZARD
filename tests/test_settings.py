"""Tests for tars/commands/settings.py — humor and honesty controls."""

from tars.commands.language import LanguageState
from tars.commands.settings import set_honesty, set_humor
from tars.utils.threading import SharedState


def _make_state():
    return SharedState(LanguageState())


def test_set_humor_parses_number():
    state = _make_state()
    result = set_humor("set humor to 90%", state)
    assert state.humor == 0.9
    assert "90%" in result


def test_set_humor_clamps_high():
    state = _make_state()
    set_humor("set humor to 200%", state)
    assert state.humor == 1.0


def test_set_humor_clamps_low():
    state = _make_state()
    set_humor("set humor to 0", state)
    assert state.humor == 0.0


def test_set_humor_no_number():
    state = _make_state()
    result = set_humor("set humor to max", state)
    assert "I need a number" in result


def test_set_humor_high_message():
    state = _make_state()
    result = set_humor("set humor to 80", state)
    assert "This should be fun" in result


def test_set_humor_low_message():
    state = _make_state()
    result = set_humor("set humor to 50", state)
    assert "Noted" in result


def test_set_honesty_parses_number():
    state = _make_state()
    result = set_honesty("set honesty to 80%", state)
    assert state.honesty == 0.8
    assert "80%" in result


def test_set_honesty_clamps():
    state = _make_state()
    set_honesty("set honesty to 150", state)
    assert state.honesty == 1.0


def test_set_honesty_no_number():
    state = _make_state()
    result = set_honesty("be more honest", state)
    assert "I need a number" in result


def test_set_honesty_high_message():
    state = _make_state()
    result = set_honesty("set honesty to 90", state)
    assert "hurt your feelings" in result


def test_set_honesty_low_message():
    state = _make_state()
    result = set_honesty("set honesty to 50", state)
    assert "gentle" in result
