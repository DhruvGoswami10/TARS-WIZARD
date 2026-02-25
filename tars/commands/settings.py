"""Runtime settings commands for TARS — humor, honesty, language."""

import re


def set_humor(command, state):
    """Parse and set humor level from command like 'set humor to 90%'."""
    match = re.search(r"(\d+)", command)
    if match:
        value = int(match.group(1))
        value = max(0, min(100, value))
        state.humor = value / 100.0
        return f"Humor set to {value}%. {'This should be fun.' if value > 70 else 'Noted.'}"
    return "I need a number. Try 'set humor to 80%'."


def set_honesty(command, state):
    """Parse and set honesty level from command like 'set honesty to 80%'."""
    match = re.search(r"(\d+)", command)
    if match:
        value = int(match.group(1))
        value = max(0, min(100, value))
        state.honesty = value / 100.0
        msg = "I might hurt your feelings." if value > 80 else "I'll be gentle."
        return f"Honesty set to {value}%. {msg}"
    return "I need a number. Try 'set honesty to 80%'."
