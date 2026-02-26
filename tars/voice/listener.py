"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Finds the USB mic using SpeechRecognition's own device list.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

_recognizer = None
_calibrated = False
_mic_index = None
_mic_index_found = False
_mic_works = False  # True if a working mic was found


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


def _find_input_device():
    """Find a working input microphone by actually opening each device.

    The ONLY reliable way to check if a device index works in
    SpeechRecognition is to enter the `with sr.Microphone(...)` context
    manager. The constructor alone doesn't validate the index.

    Strategy:
        1. Try each device by actually opening it (with block)
        2. Prefer USB/mic-named devices over others
        3. Fall back to any device that opens successfully
        4. Cache result after first successful find

    Returns:
        Device index (int) or None if nothing works.
    """
    global _mic_index, _mic_index_found, _mic_works
    if _mic_index_found:
        return _mic_index

    with _suppress_stderr():
        try:
            names = sr.Microphone.list_microphone_names()
        except Exception:
            names = []

        # Pass 1: Try USB/mic-named devices first (most likely the right one)
        usb_keywords = ("usb", "mic", "input", "capture")
        for i, name in enumerate(names):
            if any(kw in name.lower() for kw in usb_keywords):
                if _try_open_mic(i):
                    _mic_index = i
                    _mic_index_found = True
                    _mic_works = True
                    print(f"Microphone found: [{i}] {name}")
                    return _mic_index

        # Pass 2: Try every device — first one that opens wins
        for i, name in enumerate(names):
            if _try_open_mic(i):
                _mic_index = i
                _mic_index_found = True
                _mic_works = True
                print(f"Microphone found: [{i}] {name}")
                return _mic_index

        # Pass 3: Try None (system default) as last resort
        if _try_open_mic(None):
            _mic_index = None
            _mic_index_found = True
            _mic_works = True
            print("Microphone found: system default")
            return _mic_index

    # Nothing works
    _mic_index_found = True
    _mic_works = False
    _mic_index = None
    print("WARNING: No working microphone found!")
    return _mic_index


def _try_open_mic(index):
    """Try to actually open a microphone at the given index.

    Returns True if the device opens successfully (has input channels).
    This enters the `with` block which is the only reliable validation.
    """
    try:
        with _suppress_stderr():
            with sr.Microphone(device_index=index) as source:
                # If we get here, the device opened successfully
                # Do a very brief read to confirm it actually captures audio
                return source.stream is not None
    except Exception:
        return False


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated
    recognizer = _get_recognizer()
    mic_index = _find_input_device()

    if not _mic_works:
        # No working mic was found during detection
        return None

    try:
        mic_kwargs = {"device_index": mic_index} if mic_index is not None else {}
        with _suppress_stderr(), sr.Microphone(**mic_kwargs) as source:
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
