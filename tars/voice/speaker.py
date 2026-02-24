import io

import boto3
from pydub import AudioSegment, effects
from pydub.playback import play

from tars import config
from tars.commands.language import get_voice_id

# AWS Polly client — initialized lazily
_polly_client = None
_aws_available = False


def _init_polly():
    """Initialize AWS Polly client."""
    global _polly_client, _aws_available
    if not config.AWS_ACCESS_KEY or not config.AWS_SECRET_KEY:
        print("WARNING: AWS credentials not set. Voice synthesis unavailable.")
        return
    try:
        _polly_client = boto3.Session(
            aws_access_key_id=config.AWS_ACCESS_KEY,
            aws_secret_access_key=config.AWS_SECRET_KEY,
            region_name=config.AWS_REGION,
        ).client("polly")
        _aws_available = True
        print("AWS Polly initialized successfully")
    except Exception as e:
        print(f"Error initializing AWS Polly: {e}")


def initialize():
    """Initialize the speech system."""
    _init_polly()


def is_available():
    """Check if voice synthesis is available."""
    return _aws_available


def generate_speech(text, language="english"):
    """Generate speech audio from text using AWS Polly."""
    if not _aws_available:
        return None
    voice_id = get_voice_id(language)
    ssml_text = (
        f"<speak>"
        f"<prosody rate=\"{config.SPEECH_RATE}\" pitch=\"{config.SPEECH_PITCH}\">"
        f"{text}"
        f"</prosody>"
        f"</speak>"
    )
    try:
        response = _polly_client.synthesize_speech(
            Text=ssml_text,
            TextType="ssml",
            OutputFormat="mp3",
            VoiceId=voice_id,
        )
        audio_stream = response["AudioStream"].read()
        return io.BytesIO(audio_stream)
    except Exception as e:
        print(f"Error generating speech: {e}")
        return None


def modify_voice(audio_stream):
    """Apply robotic voice effects to audio."""
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
        print(f"TARS (no voice): {text}")
        return
    modified_sound = modify_voice(audio_stream)
    play_audio(modified_sound)
