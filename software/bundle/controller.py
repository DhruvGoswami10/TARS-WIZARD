# TARS Controller Input — Gamepad/keyboard control for servo movement
# See docs/controller-setup.md for finding your device event path

from evdev import InputDevice, categorize, ecodes
import mechanism
import sys

device_path = '/dev/input/event3'  # Change this to your actual path

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

                if key in ['KEY_W', 'KEY_UP']:
                    mechanism.move_forward()
                elif key in ['KEY_A', 'KEY_LEFT']:
                    mechanism.turn_left()
                elif key in ['KEY_D', 'KEY_RIGHT']:
                    mechanism.turn_right()
                elif key in ['KEY_Q']:
                    print("Exiting controller mode.")
                    break

if __name__ == "__main__":
    main()
