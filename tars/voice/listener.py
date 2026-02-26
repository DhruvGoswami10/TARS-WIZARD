"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with Google Speech API.
Bypasses sr.Microphone entirely — uses PyAudio directly with a SINGLE
persistent instance so device indices never change between calls.
A fresh stream is opened/closed per listen() call to avoid stale buffers.
"""

import contextlib
import os

import pyaudio
import speech_recognition as sr

from tars import config

_recognizer = None
_calibrated = False

# Single PyAudio instance — never terminated, keeps device indices stable.
_pa = None
_device_index = None
_device_name = None
_sample_rate = 16000
_init_done = False


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


class _StableMic(sr.AudioSource):
    """Microphone source compatible with sr.Recognizer.listen().

    Uses a shared PyAudio instance so device indices stay stable.
    Opens a fresh stream each time (via context manager) to avoid
    stale buffers that cause the mic to stop hearing.
    """

    CHUNK = 1024
    SAMPLE_WIDTH = 2  # 16-bit audio

    def __init__(self, pa_instance, device_index, sample_rate):
        self.pa = pa_instance
        self.device_index = device_index
        self.SAMPLE_RATE = sample_rate
        self.format = pyaudio.paInt16
        self.stream = None

    def __enter__(self):
        self.stream = self.pa.open(
            input=True,
            input_device_index=self.device_index,
            format=self.format,
            rate=self.SAMPLE_RATE,
            channels=1,
            frames_per_buffer=self.CHUNK,
        )
        return self

    def __exit__(self, *args):
        if self.stream:
            try:
                self.stream.stop_stream()
                self.stream.close()
            except Exception:
                pass
            self.stream = None


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


def _init_audio():
    """Initialize PyAudio ONCE and find the USB microphone.

    Creates a single PyAudio instance that lives for the entire process.
    This keeps device indices stable — no more "Device index out of range".
    """
    global _pa, _device_index, _device_name, _sample_rate, _init_done

    if _init_done:
        return _device_index is not None

    _init_done = True

    with _suppress_stderr():
        try:
            _pa = pyaudio.PyAudio()
        except Exception as e:
            print(f"PyAudio init failed: {e}")
            return False

        count = _pa.get_device_count()

        # Pass 1: Find USB/mic-named device with input channels
        usb_keywords = ("usb", "mic", "input", "capture")
        for i in range(count):
            try:
                info = _pa.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    name = info.get("name", "").lower()
                    if any(kw in name for kw in usb_keywords):
                        _device_index = i
                        _device_name = info.get("name", f"Device {i}")
                        _sample_rate = int(info.get("defaultSampleRate", 16000))
                        print(f"Microphone found: [{i}] {_device_name}")
                        return True
            except Exception:
                continue

        # Pass 2: Any device with input channels
        for i in range(count):
            try:
                info = _pa.get_device_info_by_index(i)
                if info.get("maxInputChannels", 0) > 0:
                    _device_index = i
                    _device_name = info.get("name", f"Device {i}")
                    _sample_rate = int(info.get("defaultSampleRate", 16000))
                    print(f"Microphone found: [{i}] {_device_name}")
                    return True
            except Exception:
                continue

    print("WARNING: No microphone with input channels found!")
    return False


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Opens a fresh audio stream for each call (avoids stale buffers)
    but reuses the same PyAudio instance (stable device indices).

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    global _calibrated

    if not _init_audio():
        return None

    recognizer = _get_recognizer()
    mic = _StableMic(_pa, _device_index, _sample_rate)

    try:
        with _suppress_stderr(), mic:
            if not _calibrated:
                recognizer.adjust_for_ambient_noise(mic, duration=1.0)
                _calibrated = True

            audio = recognizer.listen(
                mic,
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
    except Exception as e:
        print(f"Microphone error: {e}")
        return None
