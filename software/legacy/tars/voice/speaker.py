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


def _run_async(coro):
    """Run an async coroutine efficiently.

    Reuses event loop when possible, avoids asyncio.run() overhead.
    """
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            # Already in an async context — can't use run()
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def generate_speech(text, language="english"):
    """Generate speech audio from text using edge-tts."""
    if not _initialized:
        return None
    voice_id = get_voice_id(language)
    try:
        tmp_path = _run_async(_generate_speech_async(text, voice_id))
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


def _find_audio_player():
    """Find the best audio player — prefers PipeWire/PulseAudio for BT support."""
    # pw-play and paplay route through PipeWire/PulseAudio,
    # so they see Bluetooth speakers as the default sink.
    # aplay is ALSA-only and can't reach BT devices.
    players = [
        (["pw-play"], "PipeWire"),
        (["paplay"], "PulseAudio"),
        (["aplay", "-q"], "ALSA"),
        (["ffplay", "-nodisp", "-autoexit", "-loglevel", "quiet"], "FFmpeg"),
    ]
    for cmd, name in players:
        try:
            subprocess.run(
                [cmd[0], "--help"],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return cmd, name
        except FileNotFoundError:
            continue
    return None, None


# Cache the player on first use
_audio_player_cmd = None
_audio_player_name = None


def _play_audio_subprocess(sound):
    """Play audio via subprocess — works with Bluetooth, HDMI, USB audio."""
    global _playback_process, _audio_player_cmd, _audio_player_name
    tmp_path = None
    _speaking.set()
    try:
        # Find player once
        if _audio_player_cmd is None:
            _audio_player_cmd, _audio_player_name = _find_audio_player()
            if _audio_player_cmd is None:
                print("No audio player found. Install pipewire or pulseaudio-utils.")
                return

        # Export pydub audio to a temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
            tmp_path = tmp.name
        sound.export(tmp_path, format="wav")

        with _playback_lock:
            _playback_process = subprocess.Popen(
                _audio_player_cmd + [tmp_path],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
        _playback_process.wait()
    except Exception as e:
        print(f"Playback error: {e}")
    finally:
        with _playback_lock:
            _playback_process = None
        _speaking.clear()
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def play_audio(sound, blocking=True):
    """Play an audio segment.

    Args:
        blocking: If True, wait for playback to finish. If False, return
                  immediately (playback continues in background thread).
    """
    t = threading.Thread(target=_play_audio_subprocess, args=(sound,), daemon=True)
    t.start()
    if blocking:
        t.join()


def stop_speaking():
    """Interrupt current playback immediately."""
    with _playback_lock:
        if _playback_process is not None:
            try:
                _playback_process.terminate()
            except Exception:
                pass
    _speaking.clear()


def speak(text, language="english", blocking=True):
    """Full pipeline: generate speech, apply effects, play audio.

    Args:
        blocking: If True (default), wait for playback to finish.
                  If False, return immediately (voice pipeline uses this
                  so it can listen for interruptions while TARS speaks).
    """
    audio_stream = generate_speech(text, language)
    if audio_stream is None:
        return
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound, blocking=blocking)
