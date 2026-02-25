"""Startup status detection — checks hardware, APIs, and devices."""

from tars import config


def check_openai():
    """Check if OpenAI API key is configured."""
    if config.OPENAI_API_KEY:
        # Mask the key for display
        key = config.OPENAI_API_KEY
        masked = key[:8] + "..." + key[-4:] if len(key) > 12 else "***"
        return True, f"Configured ({masked})"
    return False, "Not configured — AI responses won't work"


def check_weather():
    """Check if weather API key is configured."""
    if config.WEATHER_API_KEY:
        return True, "Configured"
    return False, "Not configured — weather commands disabled"


def check_servos():
    """Check if servo hardware is available."""
    try:
        from tars.hardware import servos

        if servos._servo_initialized:
            return True, "PCA9685 connected"
        return False, "Simulation mode (no hardware)"
    except Exception:
        return False, "Simulation mode (no hardware)"


def check_controller():
    """Check if a game controller is available."""
    try:
        import os

        from evdev import InputDevice

        for fname in os.listdir("/dev/input"):
            if fname.startswith("event"):
                try:
                    dev = InputDevice(f"/dev/input/{fname}")
                    if any(
                        kw in dev.name.lower()
                        for kw in ("controller", "gamepad", "joystick")
                    ):
                        return True, f"Found: {dev.name}"
                except Exception:
                    continue
        return False, "No controller detected"
    except ImportError:
        return False, "evdev not installed (Pi only)"
    except Exception:
        return False, "No controller detected"


def check_microphone():
    """Check if a microphone is available."""
    try:
        import speech_recognition as sr

        mic = sr.Microphone()
        return True, f"Available ({sr.Microphone.list_microphone_names()[mic.device_index]})"
    except (ImportError, OSError, IndexError):
        return False, "No microphone detected"
    except Exception:
        return False, "No microphone detected"


def check_edge_tts():
    """Check if edge-tts is available."""
    try:
        import edge_tts  # noqa: F401

        return True, "Ready (no API key needed)"
    except ImportError:
        return False, "edge-tts not installed"


def check_camera():
    """Check if Pi Camera is available."""
    try:
        from tars.hardware import camera

        if camera.is_available():
            yolo = " + YOLO" if camera.is_yolo_available() else ""
            return True, f"Pi Camera ready{yolo}"
        return False, "Not detected (Pi only)"
    except Exception:
        return False, "Not detected (Pi only)"


def get_all_status():
    """Run all checks and return results."""
    return {
        "OpenAI API": check_openai(),
        "Voice (edge-tts)": check_edge_tts(),
        "Microphone": check_microphone(),
        "Camera": check_camera(),
        "Weather API": check_weather(),
        "Servo Controller": check_servos(),
        "Game Controller": check_controller(),
    }
