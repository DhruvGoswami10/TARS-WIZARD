"""Voice state machine for TARS.

States:
    SLEEPING  — waiting for wake word ("Hey TARS")
    LISTENING — mic active, recording user speech
    THINKING  — processing command / waiting for AI response
    SPEAKING  — playing TTS audio
"""

import enum
import threading


class VoiceState(enum.Enum):
    SLEEPING = "sleeping"
    LISTENING = "listening"
    THINKING = "thinking"
    SPEAKING = "speaking"


class VoiceStateMachine:
    """Thread-safe voice state manager."""

    def __init__(self, use_wake_word=True):
        self._state = VoiceState.SLEEPING if use_wake_word else VoiceState.LISTENING
        self._lock = threading.Lock()
        self._interrupted = False
        self._listeners = []

    @property
    def state(self):
        with self._lock:
            return self._state

    @property
    def interrupted(self):
        with self._lock:
            return self._interrupted

    def transition(self, new_state):
        """Transition to a new state."""
        with self._lock:
            old_state = self._state
            self._state = new_state
            if new_state != VoiceState.SPEAKING:
                self._interrupted = False
        for callback in self._listeners:
            callback(old_state, new_state)

    def interrupt(self):
        """Signal that TARS was interrupted while speaking."""
        with self._lock:
            if self._state == VoiceState.SPEAKING:
                self._interrupted = True
                return True
            return False

    def on_transition(self, callback):
        """Register a callback for state transitions: callback(old_state, new_state)."""
        self._listeners.append(callback)

    def is_sleeping(self):
        return self.state == VoiceState.SLEEPING

    def is_listening(self):
        return self.state == VoiceState.LISTENING

    def is_thinking(self):
        return self.state == VoiceState.THINKING

    def is_speaking(self):
        return self.state == VoiceState.SPEAKING
