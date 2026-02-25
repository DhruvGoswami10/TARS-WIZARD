"""Tests for tars/commands/movement.py — movement sequences with mocked servos."""

from unittest.mock import call, patch

from tars import config
from tars.commands import movement


@patch("tars.commands.movement.time.sleep")
@patch("tars.commands.movement.servos.set_angle")
def test_move_forward_calls_servos(mock_set, mock_sleep):
    """move_forward() drives torso and arms through the correct sequence."""
    movement.move_forward()
    channels_used = {c.args[0] for c in mock_set.call_args_list}
    assert config.CHANNEL_TORSO in channels_used
    assert config.CHANNEL_LEFT_ARM in channels_used
    assert config.CHANNEL_RIGHT_ARM in channels_used
    assert mock_set.call_count >= 5


@patch("tars.commands.movement.time.sleep")
@patch("tars.commands.movement.servos.set_angle")
def test_turn_left_calls_servos(mock_set, mock_sleep):
    """turn_left() drives servos."""
    movement.turn_left()
    assert mock_set.call_count >= 4


@patch("tars.commands.movement.time.sleep")
@patch("tars.commands.movement.servos.set_angle")
def test_turn_right_calls_servos(mock_set, mock_sleep):
    """turn_right() drives servos."""
    movement.turn_right()
    assert mock_set.call_count >= 4


@patch("tars.commands.movement.time.sleep")
@patch("tars.commands.movement.servos.set_angle")
def test_neutral_sets_all_neutral(mock_set, mock_sleep):
    """neutral() sets torso and both arms to neutral positions."""
    movement.neutral()
    mock_set.assert_any_call(config.CHANNEL_TORSO, config.NEUTRAL_POS)
    mock_set.assert_any_call(config.CHANNEL_LEFT_ARM, config.LEFT_ARM_NEUTRAL_POS)
    mock_set.assert_any_call(config.CHANNEL_RIGHT_ARM, config.RIGHT_ARM_NEUTRAL_POS)


@patch("tars.commands.movement.time.sleep")
@patch("tars.commands.movement.servos.set_angle")
def test_move_forward_ends_at_neutral(mock_set, mock_sleep):
    """move_forward() last torso command is neutral position."""
    movement.move_forward()
    # Last call should be torso to neutral
    last_torso_call = [c for c in mock_set.call_args_list if c.args[0] == config.CHANNEL_TORSO][-1]
    assert last_torso_call == call(config.CHANNEL_TORSO, config.NEUTRAL_POS)
