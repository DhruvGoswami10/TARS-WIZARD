"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with optional VAD (Voice Activity Detection)
for smarter silence detection instead of fixed timeouts.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

# Try to import webrtcvad for smarter silence detection
try:
    import webrtcvad  # noqa: F401

    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False

# Persistent recognizer — avoids recreating every call
_recognizer = None
_calibrated = False
_mic_index = None


@contextlib.contextmanager
def _suppress_stderr():
    """Suppress stderr output — silences JACK/ALSA spam from PortAudio."""
    devnull = os.open(os.devnull, os.O_WRONLY)
    old_stderr = os.dup(2)
    os.dup2(devnull, 2)
    try:
        yield
    finally:
        os.dup2(old_stderr, 2)
        os.close(devnull)
        os.close(old_stderr)


def _get_recognizer():
    """Get or create the shared recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.pause_threshold = config.VOICE_PAUSE_THRESHOLD
        _recognizer.non_speaking_duration = config.VOICE_NON_SPEAKING_DURATION
        _recognizer.operation_timeout = config.VOICE_OPERATION_TIMEOUT
    return _recognizer


def _find_mic_index(force_refresh=False):
    """Find a real microphone (skip HDMI outputs)."""
    global _mic_index
    if _mic_index is not None and not force_refresh:
        return _mic_index

    try:
        names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(names):
            name_lower = name.lower()
            if any(kw in name_lower for kw in ("usb", "mic", "input", "capture")):
                _mic_index = i
                return _mic_index
    except Exception:
        pass

    _mic_index = None
    return _mic_index


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Args:
        phrase_time_limit: Max seconds to listen for a phrase (None = no limit).

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated, _mic_index
    recognizer = _get_recognizer()

    try:
        mic_index = _find_mic_index()
        phrase_limit = phrase_time_limit or config.VOICE_PHRASE_TIME_LIMIT

        # Suppress JACK/ALSA errors that PortAudio prints to stderr
        with _suppress_stderr(), sr.Microphone(device_index=mic_index) as source:
            # Calibrate once with longer duration for better noise baseline
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=1.0)
                _calibrated = True

            audio = recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,
                phrase_time_limit=phrase_limit,
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
        _mic_index = None  # force device re-discovery next listen call
        print(f"Microphone error: {e}")
        return None
