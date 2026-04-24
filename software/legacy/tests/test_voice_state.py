"""Tests for tars/voice/voice_state.py — state machine transitions."""

from tars.voice.voice_state import VoiceState, VoiceStateMachine


def test_initial_state_with_wake_word():
    """Initial state is SLEEPING when wake word is enabled."""
    sm = VoiceStateMachine(use_wake_word=True)
    assert sm.state == VoiceState.SLEEPING


def test_initial_state_without_wake_word():
    """Initial state is LISTENING when wake word is disabled."""
    sm = VoiceStateMachine(use_wake_word=False)
    assert sm.state == VoiceState.LISTENING


def test_transition():
    """State transitions work."""
    sm = VoiceStateMachine(use_wake_word=True)
    sm.transition(VoiceState.LISTENING)
    assert sm.state == VoiceState.LISTENING
    sm.transition(VoiceState.THINKING)
    assert sm.state == VoiceState.THINKING
    sm.transition(VoiceState.SPEAKING)
    assert sm.state == VoiceState.SPEAKING


def test_interrupt_while_speaking():
    """Interrupt works during SPEAKING state."""
    sm = VoiceStateMachine(use_wake_word=False)
    sm.transition(VoiceState.SPEAKING)
    assert sm.interrupt() is True
    assert sm.interrupted is True


def test_interrupt_while_not_speaking():
    """Interrupt fails when not in SPEAKING state."""
    sm = VoiceStateMachine(use_wake_word=False)
    sm.transition(VoiceState.LISTENING)
    assert sm.interrupt() is False
    assert sm.interrupted is False


def test_interrupted_resets_on_non_speaking_transition():
    """Interrupted flag resets when transitioning away from SPEAKING."""
    sm = VoiceStateMachine(use_wake_word=False)
    sm.transition(VoiceState.SPEAKING)
    sm.interrupt()
    assert sm.interrupted is True
    sm.transition(VoiceState.LISTENING)
    assert sm.interrupted is False


def test_state_check_helpers():
    """Helper methods is_sleeping, is_listening, etc. work."""
    sm = VoiceStateMachine(use_wake_word=True)
    assert sm.is_sleeping() is True
    assert sm.is_listening() is False
    sm.transition(VoiceState.LISTENING)
    assert sm.is_listening() is True
    assert sm.is_sleeping() is False


def test_on_transition_callback():
    """Transition callbacks are fired."""
    sm = VoiceStateMachine(use_wake_word=True)
    calls = []
    sm.on_transition(lambda old, new: calls.append((old, new)))
    sm.transition(VoiceState.LISTENING)
    assert len(calls) == 1
    assert calls[0] == (VoiceState.SLEEPING, VoiceState.LISTENING)
