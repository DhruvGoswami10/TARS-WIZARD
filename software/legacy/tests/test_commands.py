"""Tests for tars/commands/router.py — command routing and dispatch."""

from unittest.mock import patch

from tars.commands.language import LanguageState
from tars.utils.threading import SharedState


def _make_state():
    return SharedState(LanguageState())


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_empty_command_returns_state(mock_chat, mock_term, mock_speaker):
    """Empty command returns state unchanged."""
    from tars.commands.router import process_command

    state = _make_state()
    result = process_command("", state)
    assert result is state
    mock_chat.get_response.assert_not_called()


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_time_command(mock_chat, mock_term, mock_speaker):
    """'what time is it' triggers time response."""
    from tars.commands.router import process_command

    state = _make_state()
    result = process_command("what time is it", state)
    assert result is state
    mock_term.print_tars.assert_called_once()
    # Should contain time format
    call_args = mock_term.print_tars.call_args[0][0]
    assert ":" in call_args


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
@patch("tars.commands.router.info")
def test_weather_command(mock_info, mock_chat, mock_term, mock_speaker):
    """'weather' triggers weather response."""
    from tars.commands.router import process_command

    mock_info.get_weather.return_value = "Sunny and 25C"
    state = _make_state()
    process_command("what's the weather", state)
    mock_info.get_weather.assert_called_once()
    mock_term.print_tars.assert_called_with("Sunny and 25C")


@patch("tars.commands.router.time.sleep")
@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_stop_command_returns_stop(mock_chat, mock_term, mock_speaker, mock_sleep):
    """'stop' command returns 'stop' string."""
    from tars.commands.router import process_command

    mock_chat.get_response.return_value = "Goodbye."
    state = _make_state()
    result = process_command("stop", state)
    assert result == "stop"


@patch("tars.commands.router.time.sleep")
@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_exit_command_returns_stop(mock_chat, mock_term, mock_speaker, mock_sleep):
    """'exit' command returns 'stop' string."""
    from tars.commands.router import process_command

    mock_chat.get_response.return_value = "Goodbye."
    state = _make_state()
    result = process_command("exit", state)
    assert result == "stop"


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_default_goes_to_chat(mock_chat, mock_term, mock_speaker):
    """Unrecognized commands go to AI chat."""
    from tars.commands.router import process_command

    mock_chat.get_response.return_value = "Very funny, human."
    state = _make_state()
    process_command("tell me a joke", state)
    mock_chat.get_response.assert_called_once()
    mock_term.print_tars.assert_called_with("Very funny, human.")


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
def test_set_humor_command(mock_chat, mock_term, mock_speaker):
    """'set humor to 80%' updates humor setting."""
    from tars.commands.router import process_command

    state = _make_state()
    process_command("set humor to 80%", state)
    assert state.humor == 0.8


@patch("tars.commands.router.speaker")
@patch("tars.commands.router.terminal")
@patch("tars.commands.router.chat")
@patch("tars.commands.router.movement")
def test_move_forward_command(mock_move, mock_chat, mock_term, mock_speaker):
    """'move forward' triggers movement."""
    from tars.commands.router import process_command

    mock_chat.get_response.return_value = "Moving."
    state = _make_state()
    process_command("move forward", state)
    mock_move.move_forward.assert_called_once()
