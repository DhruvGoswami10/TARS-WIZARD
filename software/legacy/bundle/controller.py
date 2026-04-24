# TARS Controller Input — Gamepad/keyboard control for servo movement
# Now uses shared tars/ package. This file is kept for backward compatibility.

import sys
from pathlib import Path

# Add project root to path so tars/ package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from evdev import InputDevice, categorize, ecodes  # noqa: E402

from tars.commands import movement  # noqa: E402

device_path = "/dev/input/event3"  # Change this to your actual path


def main():
    try:
        gamepad = InputDevice(device_path)
    except FileNotFoundError:
        print("Device not found. Check the event path.")
        return

    print("Controller ready. Use W/A/D or Arrow Keys. Q to Quit.")

    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY:
            key_event = categorize(event)
            if key_event.keystate == key_event.key_down:
                key = key_event.keycode

                if key in ["KEY_W", "KEY_UP"]:
                    movement.move_forward()
                elif key in ["KEY_A", "KEY_LEFT"]:
                    movement.turn_left()
                elif key in ["KEY_D", "KEY_RIGHT"]:
                    movement.turn_right()
                elif key in ["KEY_Q"]:
                    print("Exiting controller mode.")
                    break


if __name__ == "__main__":
    main()
