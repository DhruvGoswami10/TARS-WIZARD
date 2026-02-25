"""Text-to-speech for TARS — edge-tts with robotic voice effects.

Features:
    - Free TTS via edge-tts (no API key needed)
    - Robotic voice processing (band-pass filter, speedup)
    - Interruptible playback (can stop mid-sentence)
"""

import asyncio
import io
import os
import tempfile
import threading

import edge_tts
from pydub import AudioSegment, effects
from pydub.playback import play

from tars import config
from tars.commands.language import get_voice_id

_initialized = False

# Interrupt support — allows stopping playback mid-sentence
_playback_thread = None
_playback_stop = threading.Event()
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


def _play_interruptible(sound):
    """Play audio in chunks so it can be interrupted."""
    _speaking.set()
    _playback_stop.clear()

    chunk_ms = 200  # Check for interrupts every 200ms
    total_ms = len(sound)

    try:
        pos = 0
        while pos < total_ms:
            if _playback_stop.is_set():
                break
            end = min(pos + chunk_ms, total_ms)
            chunk = sound[pos:end]
            play(chunk)
            pos = end
    finally:
        _speaking.clear()


def play_audio(sound, interruptible=True):
    """Play an audio segment, optionally in an interruptible thread."""
    global _playback_thread

    if interruptible:
        _playback_thread = threading.Thread(
            target=_play_interruptible, args=(sound,), daemon=True
        )
        _playback_thread.start()
        _playback_thread.join()
    else:
        play(sound)


def stop_speaking():
    """Interrupt current playback."""
    _playback_stop.set()
    if _playback_thread and _playback_thread.is_alive():
        _playback_thread.join(timeout=1.0)


def speak(text, language="english", interruptible=True):
    """Full pipeline: generate speech, apply effects, play audio."""
    audio_stream = generate_speech(text, language)
    if audio_stream is None:
        return
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound, interruptible=interruptible)
