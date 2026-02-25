"""Text-to-speech for TARS — edge-tts with robotic voice effects.

Features:
    - Free TTS via edge-tts (no API key needed)
    - Robotic voice processing (band-pass filter, speedup)
    - Interruptible playback via subprocess (works with Bluetooth audio)
"""

import asyncio
import io
import os
import subprocess
import tempfile
import threading

import edge_tts
from pydub import AudioSegment, effects

from tars import config
from tars.commands.language import get_voice_id

_initialized = False

# Interrupt support — allows stopping playback mid-sentence
_playback_process = None
_playback_lock = threading.Lock()
_speaking = threading.Event()


def initialize():
    """Initialize the speech system."""
    global _initialized
    _initialized = True


def is_available():
    """Check if voice synthesis is available."""
    return _initialized


def is_speaking():
    """Check if TARS is currently speaking."""
    return _speaking.is_set()


async def _generate_speech_async(text, voice_id):
    """Generate speech audio using edge-tts (async)."""
    communicate = edge_tts.Communicate(
        text,
        voice_id,
        rate=config.SPEECH_RATE,
        pitch=config.SPEECH_PITCH,
    )
    with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
        tmp_path = tmp.name
    await communicate.save(tmp_path)
    return tmp_path


def generate_speech(text, language="english"):
    """Generate speech audio from text using edge-tts."""
    if not _initialized:
        return None
    voice_id = get_voice_id(language)
    try:
        tmp_path = asyncio.run(_generate_speech_async(text, voice_id))
        with open(tmp_path, "rb") as f:
            audio_data = f.read()
        os.unlink(tmp_path)
        return io.BytesIO(audio_data)
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None


def modify_voice(audio_stream):
    """Apply robotic TARS voice effects to audio (band-pass + speedup)."""
    sound = AudioSegment.from_file(audio_stream, format="mp3")
    sound = effects.speedup(sound, playback_speed=config.PLAYBACK_SPEED)
    if config.HIGH_PASS_FILTER:
        sound = sound.high_pass_filter(config.HIGH_PASS_FILTER)
    sound = effects.low_pass_filter(sound, config.LOW_PASS_FILTER)
    sound = sound - config.VOLUME_REDUCTION
    sound = sound + config.VOLUME_BOOST
    return sound


def _play_audio_subprocess(sound):
    """Play audio via subprocess — works with Bluetooth, HDMI, USB audio."""
    global _playback_process
    tmp_path = None
    _speaking.set()
    try:
        # Export pydub audio to a temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        sound.export(tmp_path, format="wav")

        # Try aplay first (ALSA — works on all Pi audio outputs including BT)
        with _playback_lock:
            _playback_process = subprocess.Popen(
                ["aplay", "-q", tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        _playback_process.wait()
    except FileNotFoundError:
        # aplay not found — try ffplay as fallback
        try:
            with _playback_lock:
                _playback_process = subprocess.Popen(
                    ["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet", tmp_path],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            _playback_process.wait()
        except FileNotFoundError:
            print("No audio player found. Install alsa-utils or ffmpeg.")
    except Exception as e:
        print(f"Playback error: {e}")
    finally:
        with _playback_lock:
            _playback_process = None
        _speaking.clear()
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def play_audio(sound, interruptible=True):
    """Play an audio segment, optionally in an interruptible thread."""
    if interruptible:
        t = threading.Thread(target=_play_audio_subprocess, args=(sound,), daemon=True)
        t.start()
        t.join()
    else:
        _play_audio_subprocess(sound)


def stop_speaking():
    """Interrupt current playback immediately."""
    with _playback_lock:
        if _playback_process is not None:
            try:
                _playback_process.terminate()
            except Exception:
                pass
    _speaking.clear()


def speak(text, language="english", interruptible=True):
    """Full pipeline: generate speech, apply effects, play audio."""
    audio_stream = generate_speech(text, language)
    if audio_stream is None:
        return
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound, interruptible=interruptible)
