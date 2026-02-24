# TARS Master Control — All-in-One Desktop Mode (DEPRECATED)
# This file is kept for backward compatibility.
# Use main.py instead:  python main.py
#
# Now uses shared tars/ package. This file provides the Tkinter GUI wrapper.

import os
import sys
import threading
import time
import tkinter as tk
from pathlib import Path
from tkinter import scrolledtext
from tkinter.font import Font

# Add project root to path so tars/ package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tars.ai import chat  # noqa: E402
from tars.commands.language import LanguageState  # noqa: E402
from tars.commands.movement import (  # noqa: E402
    move_forward,
    neutral,
    turn_left,
    turn_right,
)
from tars.commands.router import process_command  # noqa: E402
from tars.hardware import servos  # noqa: E402
from tars.voice import listener, speaker  # noqa: E402

# Try to import controller-related modules
try:
    from evdev import InputDevice, ecodes

    CONTROLLER_AVAILABLE = True
except ImportError:
    print("Controller library (evdev) not found. Controller support disabled.")
    CONTROLLER_AVAILABLE = False

# ─── CONTROLLER ──────────────────────────────────────────────
controller = None
if CONTROLLER_AVAILABLE:
    try:
        devices = [
            InputDevice(path)
            for path in os.listdir("/dev/input")
            if path.startswith("event")
        ]
        for device in devices:
            if any(
                kw in device.name.lower()
                for kw in ("controller", "gamepad", "joystick")
            ):
                controller = device
                print(f"Controller found: {device.name}")
                break
        if not controller:
            print("Controller not found. Voice commands will still work.")
    except Exception as e:
        print(f"Error initializing controller: {e}")
        print("Voice commands will still work.")
else:
    print("Controller support not available. Voice commands will still work.")


# ─── CONTROLLER INPUT ────────────────────────────────────────
def read_controller_input():
    if not CONTROLLER_AVAILABLE or not controller:
        return None
    try:
        event = controller.read_one()
        if event and event.type == ecodes.EV_KEY and event.value == 1:
            if event.code == ecodes.BTN_A:
                return "move_forward"
            elif event.code == ecodes.BTN_B:
                return "turn_right"
            elif event.code == ecodes.BTN_X:
                return "turn_left"
            elif event.code == ecodes.BTN_Y:
                return "neutral"
            elif event.code == ecodes.BTN_START:
                return "stop"
        return None
    except Exception as e:
        print(f"Error reading controller: {e}")
        return None


def process_controller_command(command, state):
    action_map = {
        "move_forward": ("Moving forward", move_forward),
        "turn_left": ("Turning left", turn_left),
        "turn_right": ("Turning right", turn_right),
        "neutral": ("Neutral position", neutral),
    }
    if command in action_map:
        prompt, action = action_map[command]
        action(state.current_language)
        response = chat.get_response(
            prompt,
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)
    elif command == "stop":
        response = chat.get_response(
            "Goodbye",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)
        time.sleep(1)
        return "stop"
    return state


def controller_thread_function(state):
    while True:
        command = read_controller_input()
        if command:
            new_state = process_controller_command(command, state)
            if new_state == "stop":
                sys.exit()
            else:
                state = new_state
        time.sleep(0.01)


# ─── TKINTER UI ──────────────────────────────────────────────
class TARSTerminalUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TARS Terminal Interface")
        self.root.configure(bg="black")
        self.root.geometry("800x600")
        self.terminal_font = Font(family="Courier New", size=10)

        self.main_frame = tk.Frame(root, bg="black")
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.terminal_output = scrolledtext.ScrolledText(
            self.main_frame,
            bg="black",
            fg="#00ff00",
            insertbackground="#00ff00",
            selectbackground="#005500",
            font=self.terminal_font,
            wrap=tk.WORD,
        )
        self.terminal_output.pack(fill=tk.BOTH, expand=True, pady=(0, 10))
        self.terminal_output.config(state=tk.DISABLED)

        self.input_frame = tk.Frame(self.main_frame, bg="black")
        self.input_frame.pack(fill=tk.X, expand=False)

        self.prompt_label = tk.Label(
            self.input_frame,
            text="TARS> ",
            bg="black",
            fg="#00ff00",
            font=self.terminal_font,
        )
        self.prompt_label.pack(side=tk.LEFT)

        self.input_entry = tk.Entry(
            self.input_frame,
            bg="black",
            fg="#00ff00",
            insertbackground="#00ff00",
            font=self.terminal_font,
            relief=tk.FLAT,
            highlightbackground="#00ff00",
            highlightthickness=1,
        )
        self.input_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.input_entry.focus_set()
        self.input_entry.bind("<Return>", self.process_input)

        self.status_var = tk.StringVar()
        self.status_var.set("TARS ready")
        self.status_bar = tk.Label(
            self.root,
            textvariable=self.status_var,
            bg="black",
            fg="#888888",
            font=("Courier New", 9),
            anchor=tk.W,
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.state = LanguageState()
        self.command_history = []
        self.history_index = 0
        self.listening = False

        self.write_to_terminal("TARS Terminal Interface Initialized\n")
        self.write_to_terminal("Type a command or speak to interact\n")
        self.write_to_terminal("-" * 50 + "\n")
        self.root.after(1000, self.initialize_robot)

    def write_to_terminal(self, text):
        self.terminal_output.config(state=tk.NORMAL)
        self.terminal_output.insert(tk.END, text)
        self.terminal_output.see(tk.END)
        self.terminal_output.config(state=tk.DISABLED)

    def initialize_robot(self):
        self.write_to_terminal("Initializing robot to neutral position...\n")
        neutral()
        self.write_to_terminal("Robot initialized. Ready for commands.\n")
        if CONTROLLER_AVAILABLE and controller:
            self.start_controller_thread()
            self.write_to_terminal(f"Controller found: {controller.name}\n")
        else:
            self.write_to_terminal("No controller found.\n")

    def start_controller_thread(self):
        self.controller_thread = threading.Thread(
            target=controller_thread_function,
            args=(self.state,),
        )
        self.controller_thread.daemon = True
        self.controller_thread.start()
        self.write_to_terminal("Controller thread started\n")

    def process_input(self, event=None):
        command = self.input_entry.get().strip()
        if not command:
            return
        self.command_history.append(command)
        self.history_index = len(self.command_history)
        self.input_entry.delete(0, tk.END)
        self.write_to_terminal(f"You: {command}\n")
        threading.Thread(
            target=self.execute_command, args=(command,), daemon=True
        ).start()

    def execute_command(self, command):
        self.root.after(0, lambda: self.status_var.set("Processing command..."))
        result = process_command(command, self.state)
        if result == "stop":
            self.root.after(1000, self.root.destroy)
            return
        self.state = result
        self.root.after(0, lambda: self.status_var.set("Ready"))

    def send_command(self, command):
        self.input_entry.delete(0, tk.END)
        self.input_entry.insert(0, command)
        self.process_input()


# ─── MAIN ────────────────────────────────────────────────────
original_print = print
ui_instance = None


def print_override(message):
    if ui_instance:
        ui_instance.write_to_terminal(message + "\n")
    original_print(message)


def speak_override(text, language="english"):
    if ui_instance:
        ui_instance.write_to_terminal(f"TARS: {text}\n")
    speaker.speak(text, language)


def continuous_listening():
    while True:
        command = listener.listen()
        if command:
            if ui_instance:
                ui_instance.write_to_terminal(f"You: {command}\n")
                ui_instance.execute_command(command)
        time.sleep(0.1)


def main():
    global ui_instance, print, speak  # noqa: F841

    # Initialize subsystems
    servos.initialize()
    speaker.initialize()
    chat.initialize()

    original_speak = speaker.speak
    print = print_override  # noqa: F841

    # Override speaker.speak for GUI integration
    speaker.speak = speak_override

    root = tk.Tk()
    ui = TARSTerminalUI(root)
    ui_instance = ui

    try:
        threading.Thread(target=continuous_listening, daemon=True).start()
        root.mainloop()
    except KeyboardInterrupt:
        pass
    finally:
        print = original_print  # noqa: F841
        speaker.speak = original_speak


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nProgram terminated by user")
        sys.exit(0)
