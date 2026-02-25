"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with optional VAD (Voice Activity Detection)
for smarter silence detection instead of fixed timeouts.
"""

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


def _get_recognizer():
    """Get or create the shared recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        _recognizer.pause_threshold = 2.0 if VAD_AVAILABLE else 1.5
    return _recognizer


def _find_mic_index():
    """Find a real microphone (skip HDMI outputs)."""
    try:
        names = sr.Microphone.list_microphone_names()
        for i, name in enumerate(names):
            name_lower = name.lower()
            if any(kw in name_lower for kw in ("usb", "mic", "input", "capture")):
                return i
    except Exception:
        pass
    return None


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Args:
        phrase_time_limit: Max seconds to listen for a phrase (None = no limit).

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated
    recognizer = _get_recognizer()

    try:
        mic_index = _find_mic_index()
        with sr.Microphone(device_index=mic_index) as source:
            # Only calibrate once — not every listen cycle
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                _calibrated = True

            audio = recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,
                phrase_time_limit=phrase_time_limit,
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
