"""Speech recognition for TARS — listens for voice commands.

Uses SpeechRecognition with optional VAD (Voice Activity Detection)
for smarter silence detection instead of fixed timeouts.
"""

import speech_recognition as sr

from tars import config

# Try to import webrtcvad for smarter silence detection
try:
    import webrtcvad  # noqa: F401

    VAD_AVAILABLE = True
except ImportError:
    VAD_AVAILABLE = False


def listen(phrase_time_limit=None):
    """Listen for a voice command via microphone.

    Args:
        phrase_time_limit: Max seconds to listen for a phrase (None = no limit).

    Returns:
        Lowercase string of recognized speech, or None on failure.
    """
    recognizer = sr.Recognizer()

    # Tune recognizer for better results
    recognizer.dynamic_energy_threshold = True
    recognizer.pause_threshold = 1.5  # seconds of silence before considering phrase complete

    if VAD_AVAILABLE:
        # With VAD, we can use longer pause threshold — it's smarter about silence
        recognizer.pause_threshold = 2.0

    try:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.5)
            audio = recognizer.listen(
                source,
                timeout=config.LISTEN_TIMEOUT,
                phrase_time_limit=phrase_time_limit,
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
