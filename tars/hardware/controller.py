"""Game controller auto-detection for TARS.

Auto-scans /dev/input/ for gamepads on Linux/Pi.
Gracefully returns None on Windows/Mac or if no controller found.
"""

_controller = None
_controller_name = None


def detect():
    """Auto-detect a game controller. Returns (device, name) or (None, None)."""
    global _controller, _controller_name

    try:
        import os

        from evdev import InputDevice
    except ImportError:
        return None, None

    try:
        for fname in os.listdir("/dev/input"):
            if fname.startswith("event"):
                try:
                    dev = InputDevice(f"/dev/input/{fname}")
                    if any(
                        kw in dev.name.lower()
                        for kw in ("controller", "gamepad", "joystick")
                    ):
                        _controller = dev
                        _controller_name = dev.name
                        return dev, dev.name
                except Exception:
                    continue
    except Exception:
        pass

    return None, None


def get_controller():
    """Get the detected controller (or None)."""
    return _controller


def get_name():
    """Get the detected controller name (or None)."""
    return _controller_name


def is_available():
    """Check if a controller is available."""
    return _controller is not None
