"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Optimized for low latency: mic stays open, device index cached.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

# Persistent state — avoids recreating every listen cycle
_recognizer = None
_mic_index = None
_mic_index_found = False
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
        yield  # If fd manipulation fails, just continue without suppression


def _get_recognizer():
    """Get or create the shared recognizer instance."""
    global _recognizer
    if _recognizer is None:
        _recognizer = sr.Recognizer()
        _recognizer.dynamic_energy_threshold = True
        # Lower = detects end-of-speech faster (snappier response)
        _recognizer.pause_threshold = 0.8
        _recognizer.non_speaking_duration = 0.3
        # Lower energy ratio = more sensitive to quiet speech
        _recognizer.energy_threshold = 300
    return _recognizer


def _get_mic_index():
    """Get cached mic index (found once, reused forever)."""
    global _mic_index, _mic_index_found
    if _mic_index_found:
        return _mic_index

    # Suppress stderr during PyAudio init (JACK spam source)
    with _suppress_stderr():
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            device_count = pa.get_device_count()

            # Search for a real mic by checking device info
            for i in range(device_count):
                try:
                    info = pa.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        name = info.get("name", "").lower()
                        if any(kw in name for kw in ("usb", "mic", "input", "capture")):
                            _mic_index = i
                            _mic_index_found = True
                            pa.terminate()
                            return _mic_index
                except Exception:
                    continue

            # No keyword match — use first input device
            for i in range(device_count):
                try:
                    info = pa.get_device_info_by_index(i)
                    if info.get("maxInputChannels", 0) > 0:
                        _mic_index = i
                        _mic_index_found = True
                        pa.terminate()
                        return _mic_index
                except Exception:
                    continue

            pa.terminate()
        except Exception:
            pass

    # Fallback: let SpeechRecognition pick default
    _mic_index_found = True
    _mic_index = None
    return _mic_index


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Args:
        phrase_time_limit: Max seconds to listen for a phrase (None = use default).

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated
    recognizer = _get_recognizer()
    mic_index = _get_mic_index()

    try:
        # Suppress stderr only on first open (JACK errors happen on PyAudio init)
        if not _calibrated:
            ctx = _suppress_stderr()
        else:
            ctx = contextlib.nullcontext()

        with ctx, sr.Microphone(device_index=mic_index) as source:
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
