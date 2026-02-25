"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Optimized for low latency: device cached, stderr suppressed.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

# Persistent state — avoids recreating every listen cycle
_recognizer = None
_calibrated = False


@contextlib.contextmanager
def _suppress_stderr():
    """Suppress stderr — silences JACK/ALSA spam from PortAudio."""
    try:
        devnull = os.open(os.devnull, os.O_WRONLY)
        old_stderr = os.dup(2)
        os.dup2(devnull, 2)
        try:
            yield
        finally:
            os.dup2(old_stderr, 2)
            os.close(devnull)
            os.close(old_stderr)
    except OSError:
        yield


def _get_recognizer():
    """Get or create the shared recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        # pause_threshold: seconds of silence before phrase is considered done.
        # Too low = cuts off mid-sentence. Too high = slow response.
        _recognizer.pause_threshold = 1.2
        _recognizer.non_speaking_duration = 0.5
        _recognizer.energy_threshold = 300
    return _recognizer


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated
    recognizer = _get_recognizer()

    try:
        # Always suppress stderr — JACK errors come from Microphone() init
        with _suppress_stderr(), sr.Microphone() as source:
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                _calibrated = True

            audio = recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,
                phrase_time_limit=phrase_time_limit or 10,
            )
            command = recognizer.recognize_google(audio)
            return command.lower()
    except sr.UnknownValueError:
        return None
    except sr.WaitTimeoutError:
        return None
    except sr.RequestError:
        print("Speech service unavailable.")
        return None
    except OSError as e:
        print(f"Microphone error: {e}")
        return None
