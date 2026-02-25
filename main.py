#!/usr/bin/env python3
"""TARS-WIZARD v2.0 — Single entry point.

Usage:
    python main.py              # Interactive mode (text + voice, always listening)
    python main.py --text-only  # Text-only mode (no mic/speaker)
    python main.py --wake-word  # Require "Hey TARS" before listening
    python main.py --help       # Show help
"""

import argparse
import sys
import threading
import time

# Suppress ALSA/JACK error spam before any audio library imports
try:
    import ctypes

    _ERROR_HANDLER = ctypes.CFUNCTYPE(None, ctypes.c_char_p, ctypes.c_int,
                                      ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p)

    def _alsa_error_handler(filename, line, function, err, fmt):
        pass  # Swallow all ALSA errors

    _c_error_handler = _ERROR_HANDLER(_alsa_error_handler)
    ctypes.cdll.LoadLibrary("libasound.so.2").snd_lib_error_set_handler(_c_error_handler)
except Exception:
    pass  # Not on Linux or no ALSA — that's fine

from tars.ai import chat
from tars.commands.language import LanguageState
from tars.commands.movement import neutral
from tars.commands.router import process_command
from tars.hardware import camera, servos
from tars.ui import terminal
from tars.utils.logging import setup as setup_logging
from tars.utils.threading import SharedState, is_shutting_down, request_shutdown, shutdown_event
from tars.voice import listener, speaker
from tars.voice.voice_state import VoiceState, VoiceStateMachine
from tars.voice.wake_word import WakeWordDetector


def first_run_check():
    """Check if .env exists; if not, guide the user through setup."""
    from pathlib import Path

    from tars import config

    env_path = Path(config._PROJECT_ROOT) / ".env"
    if env_path.exists():
        return

    terminal.print_system("First run detected — let's set up your API keys.")
    terminal.print_system("You can always edit .env later to change these.\n")

    cerebras_key = input("Cerebras API Key (primary AI — free at cloud.cerebras.ai, Enter to skip): ").strip()
    openai_key = input("OpenAI API Key (fallback AI, press Enter to skip): ").strip()
    weather_key = input("OpenWeatherMap API Key (optional, press Enter to skip): ").strip()
    city = input("Your city name for weather (optional, press Enter to skip): ").strip()

    lines = []
    lines.append(f"CEREBRAS_API_KEY={cerebras_key}")
    lines.append(f"OPENAI_API_KEY={openai_key}")
    lines.append(f"WEATHER_API_KEY={weather_key}")
    lines.append(f"CITY_NAME={city}")

    with open(env_path, "w") as f:
        f.write("\n".join(lines) + "\n")

    terminal.print_system(f"\nSaved to {env_path}")
    terminal.print_system("Restart TARS to load the new keys.\n")
    sys.exit(0)


def voice_pipeline_thread(state, voice_sm, use_wake_word=False):
    """Full voice pipeline: wake word → listen → think → speak → repeat."""
    wake_detector = WakeWordDetector() if use_wake_word else None
    wake_prompt_shown = False

    while not is_shutting_down():
        try:
            # SLEEPING: Wait for wake word (or skip if no wake word mode)
            if use_wake_word:
                voice_sm.transition(VoiceState.SLEEPING)
                if not wake_prompt_shown:
                    terminal.print_system('Say "Hey TARS" or press Enter...')
                    wake_prompt_shown = True
                detected = wake_detector.listen_for_wake_word(shutdown_event)
                if not detected or is_shutting_down():
                    continue
                terminal.print_system("Wake word detected!")
                wake_prompt_shown = False  # Show again after next command

            # LISTENING: Record user speech
            voice_sm.transition(VoiceState.LISTENING)
            command = listener.listen()

            if not command or is_shutting_down():
                continue

            terminal.print_user(command)

            # THINKING: Process command
            voice_sm.transition(VoiceState.THINKING)
            result = process_command(command, state)

            if result == "stop":
                request_shutdown()
                return

        except Exception as e:
            terminal.print_error(f"Voice pipeline error: {e}")

        time.sleep(0.1)


def controller_thread(state):
    """Listen for game controller input in background."""
    try:
        import os

        from evdev import InputDevice, ecodes
    except ImportError:
        return

    # Find controller
    controller = None
    try:
        for fname in os.listdir("/dev/input"):
            if fname.startswith("event"):
                try:
                    dev = InputDevice(f"/dev/input/{fname}")
                    if any(
                        kw in dev.name.lower()
                        for kw in ("controller", "gamepad", "joystick")
                    ):
                        controller = dev
                        terminal.print_system(f"Controller: {dev.name}")
                        break
                except Exception:
                    continue
    except Exception:
        return

    if not controller:
        return

    from tars.commands.movement import move_forward, neutral, turn_left, turn_right

    button_actions = {
        ecodes.BTN_A: ("move_forward", move_forward),
        ecodes.BTN_X: ("turn_left", turn_left),
        ecodes.BTN_B: ("turn_right", turn_right),
        ecodes.BTN_Y: ("neutral", neutral),
    }

    while not is_shutting_down():
        try:
            event = controller.read_one()
            if event and event.type == ecodes.EV_KEY and event.value == 1:
                if event.code == ecodes.BTN_START:
                    request_shutdown()
                    return
                if event.code in button_actions:
                    name, action = button_actions[event.code]
                    action(state.current_language)
        except Exception:
            pass
        time.sleep(0.01)


def text_input_loop(state):
    """Main text input loop."""
    while not is_shutting_down():
        command = terminal.get_input()

        if command is None:
            # Ctrl+C or EOF
            request_shutdown()
            break

        if not command:
            continue

        if command.lower() in ("help", "?"):
            terminal.print_help()
            continue

        if command.lower() == "settings":
            terminal.print_settings(state)
            continue

        terminal.print_user(command)
        try:
            result = process_command(command, state)
        except Exception as e:
            terminal.print_error(f"Command failed: {e}")
            continue

        if result == "stop":
            request_shutdown()
            break


def main():
    parser = argparse.ArgumentParser(description="TARS-WIZARD v2.0")
    parser.add_argument(
        "--text-only",
        action="store_true",
        help="Text-only mode (no microphone or speaker)",
    )
    parser.add_argument(
        "--wake-word",
        action="store_true",
        help="Enable wake word detection (say 'Hey TARS' to activate)",
    )
    args = parser.parse_args()

    # Set up logging
    setup_logging()

    # First-run setup wizard
    first_run_check()

    # Print startup UI
    terminal.print_banner()
    terminal.console.print()

    # Initialize subsystems
    terminal.print_system("Initializing...")
    servos.initialize()
    speaker.initialize()
    chat.initialize()
    camera.initialize()

    # Show system status
    terminal.print_status_panel()
    terminal.console.print()

    # Create shared state
    lang_state = LanguageState()
    state = SharedState(lang_state, text_only=args.text_only)

    # Create voice state machine
    use_wake_word = not args.text_only and args.wake_word
    voice_sm = VoiceStateMachine(use_wake_word=use_wake_word)

    # Initialize servos to neutral
    neutral()

    # Print help hint
    terminal.print_system('Type "help" for commands, or just talk to TARS.\n')

    # Start background threads
    threads = []

    if not args.text_only:
        voice_thread = threading.Thread(
            target=voice_pipeline_thread,
            args=(state, voice_sm, use_wake_word),
            daemon=True,
        )
        voice_thread.start()
        threads.append(voice_thread)

    ctrl_thread = threading.Thread(
        target=controller_thread,
        args=(state,),
        daemon=True,
    )
    ctrl_thread.start()
    threads.append(ctrl_thread)

    # Main text input loop
    try:
        text_input_loop(state)
    except KeyboardInterrupt:
        pass
    finally:
        terminal.print_system("\nShutting down...")
        request_shutdown()

        # Stop any ongoing speech
        speaker.stop_speaking()

        # Clean up camera
        camera.cleanup()

        # Return servos to neutral position
        try:
            neutral()
            terminal.print_system("Servos returned to neutral.")
        except Exception:
            pass

        # Wait briefly for threads to finish
        shutdown_event.wait(timeout=0.5)
        terminal.print_system("Goodbye.")


if __name__ == "__main__":
    main()
