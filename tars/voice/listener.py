"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Finds the USB mic by scanning PyAudio for input-capable devices.
"""

import contextlib
import os

import speech_recognition as sr

from tars import config

_recognizer = None
_calibrated = False
_mic_index = None
_mic_index_found = False


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
    """Find the first device with input channels (i.e. a real microphone).

    The default device on Pi often has 0 input channels (HDMI output),
    so we must scan explicitly. Caches result after first call.
    """
    global _mic_index, _mic_index_found
    if _mic_index_found:
        return _mic_index

    with _suppress_stderr():
        try:
            import pyaudio
            pa = pyaudio.PyAudio()
            for i in range(pa.get_device_count()):
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

    _mic_index_found = True
    _mic_index = None
    return _mic_index


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated
    recognizer = _get_recognizer()
    mic_index = _find_input_device()

    try:
        with _suppress_stderr(), sr.Microphone(device_index=mic_index) as source:
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
