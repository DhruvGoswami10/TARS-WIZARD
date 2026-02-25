"""Wake word detection for TARS — "Hey TARS" trigger.

Uses openwakeword for local, offline wake word detection.
Falls back to keyboard trigger if openwakeword is not installed.
"""

import threading
import time

try:
    import pyaudio

    PYAUDIO_AVAILABLE = True
except ImportError:
    PYAUDIO_AVAILABLE = False

try:
    from openwakeword.model import Model as OWWModel
    from openwakeword.utils import download_models as oww_download

    OWW_AVAILABLE = True
except ImportError:
    OWW_AVAILABLE = False

# Audio stream settings for wake word detection
CHUNK_SIZE = 1280  # ~80ms at 16kHz
SAMPLE_RATE = 16000
FORMAT_INT16 = 8  # pyaudio.paInt16


class WakeWordDetector:
    """Detects 'Hey TARS' wake word using openwakeword."""

    def __init__(self, threshold=0.5):
        self.threshold = threshold
        self._model = None
        self._stream = None
        self._audio = None
        self._available = False

        if OWW_AVAILABLE and PYAUDIO_AVAILABLE:
            try:
                # Download models if not already present
                print("Checking wake word models...")
                oww_download()

                # Use the built-in "hey_jarvis" model as closest match to "Hey TARS"
                # Custom wake word models can be trained at https://github.com/dscripka/openwakeword
                self._model = OWWModel(
                    wakeword_models=["hey_jarvis"],
                    inference_framework="onnx",
                )
                self._available = True
                print("Wake word detection ready (openwakeword)")
            except Exception as e:
                print(f"Wake word init failed: {e}")
        else:
            missing = []
            if not OWW_AVAILABLE:
                missing.append("openwakeword")
            if not PYAUDIO_AVAILABLE:
                missing.append("pyaudio")
            print(f"Wake word unavailable (missing: {', '.join(missing)})")

    @property
    def available(self):
        return self._available

    def listen_for_wake_word(self, shutdown_event=None):
        """Block until wake word is detected. Returns True on detection, False on shutdown."""
        if not self._available:
            # Fallback: wait for Enter key press
            return self._keyboard_fallback(shutdown_event)

        try:
            self._audio = pyaudio.PyAudio()
            self._stream = self._audio.open(
                format=FORMAT_INT16,
                channels=1,
                rate=SAMPLE_RATE,
                input=True,
                frames_per_buffer=CHUNK_SIZE,
            )
        except Exception as e:
            print(f"Mic error for wake word: {e}")
            return self._keyboard_fallback(shutdown_event)

        try:
            while shutdown_event is None or not shutdown_event.is_set():
                audio_data = self._stream.read(CHUNK_SIZE, exception_on_overflow=False)
                prediction = self._model.predict(audio_data)

                # Check all wake word models for activation
                for model_name, score in prediction.items():
                    if score > self.threshold:
                        self._model.reset()
                        return True

                time.sleep(0.01)
        except Exception:
            pass
        finally:
            self._cleanup()

        return False

    def _keyboard_fallback(self, shutdown_event=None):
        """Fallback: wait for Enter key in a separate thread."""
        result = [False]
        done = threading.Event()

        def wait_for_enter():
            try:
                input()
                result[0] = True
            except (EOFError, KeyboardInterrupt):
                pass
            done.set()

        t = threading.Thread(target=wait_for_enter, daemon=True)
        t.start()

        # Wait for either Enter or shutdown
        while not done.is_set():
            if shutdown_event and shutdown_event.is_set():
                return False
            done.wait(timeout=0.2)

        return result[0]

    def _cleanup(self):
        """Clean up audio resources."""
        if self._stream:
            try:
                self._stream.stop_stream()
                self._stream.close()
            except Exception:
                pass
            self._stream = None
        if self._audio:
            try:
                self._audio.terminate()
            except Exception:
                pass
            self._audio = None
