import asyncio
import io
import tempfile

import edge_tts
from pydub import AudioSegment, effects
from pydub.playback import play

from tars import config
from tars.commands.language import get_voice_id

_initialized = False


def initialize():
    """Initialize the speech system."""
    global _initialized
    _initialized = True
    print("Edge TTS initialized (no API key required)")


def is_available():
    """Check if voice synthesis is available."""
    return _initialized


async def _generate_speech_async(text, voice_id):
    """Generate speech audio using edge-tts (async)."""
    communicate = edge_tts.Communicate(
        text,
        voice_id,
        rate=config.SPEECH_RATE,
        pitch=config.SPEECH_PITCH,
    )
    # edge-tts writes to a file; use a temp file then read it back
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
        # Clean up temp file
        import os

        os.unlink(tmp_path)
        return io.BytesIO(audio_data)
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None


def modify_voice(audio_stream):
    """Apply robotic TARS voice effects to audio."""
    sound = AudioSegment.from_file(audio_stream, format="mp3")
    sound = effects.speedup(sound, playback_speed=config.PLAYBACK_SPEED)
    sound = effects.low_pass_filter(sound, config.LOW_PASS_FILTER)
    sound = sound - config.VOLUME_REDUCTION
    sound = sound + config.VOLUME_BOOST
    return sound


def play_audio(sound):
    """Play an audio segment."""
    play(sound)


def speak(text, language="english"):
    """Full pipeline: generate speech, apply effects, play audio."""
    print(f"TARS: {text}")
    audio_stream = generate_speech(text, language)
    if audio_stream is None:
        return
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound)
