"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Opens the USB mic ONCE and keeps it alive to avoid PyAudio
device index instability between reinitializations.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

_recognizer = None
_calibrated = False

# Persistent mic — opened once, never closed between listen() calls.
# This avoids PyAudio device count changing on every reinitialization.
_mic = None
_mic_source = None
_mic_ready = False
_mic_attempted = False


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
        _recognizer.pause_threshold = 1.2
        _recognizer.non_speaking_duration = 0.5
        _recognizer.energy_threshold = 300
    return _recognizer


def _open_mic():
    """Find and open the microphone ONCE. Keeps it alive for all listen() calls.

    The key insight: PyAudio's device count is unstable — it can change
    between reinitializations. So we open the mic once and never close it.
    This way the device index is validated exactly once at open time.
    """
    global _mic, _mic_source, _mic_ready, _mic_attempted

    if _mic_attempted:
        return _mic_ready

    _mic_attempted = True

    with _suppress_stderr():
        try:
            names = sr.Microphone.list_microphone_names()
        except Exception:
            names = []

        # Build candidate list: USB/mic-named devices first, then all others
        usb_keywords = ("usb", "mic", "input", "capture")
        candidates = []
        others = []
        for i, name in enumerate(names):
            if any(kw in name.lower() for kw in usb_keywords):
                candidates.append((i, name))
            else:
                others.append((i, name))
        candidates.extend(others)
        candidates.append((None, "system default"))

        for idx, name in candidates:
            try:
                if idx is not None:
                    mic = sr.Microphone(device_index=idx)
                else:
                    mic = sr.Microphone()

                # Actually open the mic (enters the context manager)
                # This is where "Device index out of range" would throw
                source = mic.__enter__()

                # Success — keep it alive
                _mic = mic
                _mic_source = source
                _mic_ready = True
                print(f"Microphone opened: [{idx}] {name}")
                return True
            except Exception:
                continue

    print("WARNING: No working microphone found!")
    return False


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated

    # Open mic on first call (stays open forever)
    if not _open_mic():
        return None

    recognizer = _get_recognizer()

    try:
        with _suppress_stderr():
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(_mic_source, duration=1.0)
                _calibrated = True

            audio = recognizer.listen(
                _mic_source,
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
        # Mic may have disconnected — allow retry on next call
        _reset_mic()
        return None


def _reset_mic():
    """Reset mic state so next listen() will try to reopen."""
    global _mic, _mic_source, _mic_ready, _mic_attempted, _calibrated
    if _mic is not None:
        try:
            _mic.__exit__(None, None, None)
        except Exception:
            pass
    _mic = None
    _mic_source = None
    _mic_ready = False
    _mic_attempted = False
    _calibrated = False
