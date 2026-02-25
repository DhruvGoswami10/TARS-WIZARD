"""Thread-safe utilities for TARS — event bus, shared state, graceful shutdown."""

import threading


# Global shutdown signal — set this to stop all threads gracefully
shutdown_event = threading.Event()


class SharedState:
    """Thread-safe wrapper for LanguageState and other shared data."""

    def __init__(self, state, text_only=False):
        self._state = state
        self._lock = threading.Lock()
        self.text_only = text_only

    @property
    def current_language(self):
        with self._lock:
            return self._state.current_language

    @current_language.setter
    def current_language(self, value):
        with self._lock:
            self._state.current_language = value

    @property
    def humor(self):
        with self._lock:
            return self._state.humor

    @humor.setter
    def humor(self, value):
        with self._lock:
            self._state.humor = value

    @property
    def honesty(self):
        with self._lock:
            return self._state.honesty

    @honesty.setter
    def honesty(self, value):
        with self._lock:
            self._state.honesty = value


def is_shutting_down():
    """Check if shutdown has been requested."""
    return shutdown_event.is_set()


def request_shutdown():
    """Signal all threads to stop."""
    shutdown_event.set()
