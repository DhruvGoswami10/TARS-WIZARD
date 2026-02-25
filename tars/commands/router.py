import time

from tars.ai import chat
from tars.commands import info, language, movement
from tars.hardware import camera
from tars.ui import terminal
from tars.voice import speaker


def _respond(text, lang):
    """Print response to terminal and speak it."""
    terminal.print_tars(text)
    try:
        speaker.speak(text, lang)
    except Exception as e:
        terminal.print_error(f"Speech error: {e}")


def process_command(command, state):
    """Route a voice/text command to the appropriate handler.

    Returns the updated state, or "stop" to signal shutdown.
    """
    if not command:
        return state

    cmd = command.lower()

    # Language switching
    if "speak" in cmd and any(lang in cmd for lang in language.get_supported_languages()):
        for lang in language.get_supported_languages():
            if lang in cmd:
                state.current_language = lang
                response = chat.get_response(
                    "Confirm language change",
                    honesty=state.honesty,
                    humor=state.humor,
                    target_language=state.current_language,
                )
                _respond(response, state.current_language)
                return state

    # Movement commands
    if "move forward" in cmd or "take 2 steps" in cmd:
        movement.move_forward(state.current_language)
        response = chat.get_response(
            "Moving forward",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)

    elif "turn left" in cmd:
        movement.turn_left(state.current_language)
        response = chat.get_response(
            "Turning left",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)

    elif "turn right" in cmd:
        movement.turn_right(state.current_language)
        response = chat.get_response(
            "Turning right",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)

    # Shutdown
    elif "stop" in cmd or cmd in ("exit", "quit"):
        response = chat.get_response(
            "Goodbye",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)
        time.sleep(1)
        return "stop"

    # Info commands
    elif "time" in cmd or "date" in cmd:
        response = info.get_current_time()
        _respond(response, state.current_language)

    elif "weather" in cmd:
        response = info.get_weather()
        _respond(response, state.current_language)

    # Camera / vision commands
    elif any(phrase in cmd for phrase in ("what do you see", "look around", "describe")):
        if not camera.is_available():
            _respond("My eyes are offline. No camera detected.", state.current_language)
        else:
            _respond("Let me take a look...", state.current_language)
            response = camera.describe_scene()
            _respond(response, state.current_language)

    elif "how many people" in cmd:
        if not camera.is_available():
            _respond("I can't see anyone — no camera.", state.current_language)
        elif not camera.is_yolo_available():
            _respond("My detection system is offline. I need ultralytics installed.", state.current_language)
        else:
            count = camera.count_people()
            if count == 0:
                response = "I don't see anyone. Either I'm alone, or everyone's hiding."
            elif count == 1:
                response = "I see one person. Just you and me, I guess."
            else:
                response = f"I count {count} people. That's {count} more than I'd prefer."
            _respond(response, state.current_language)

    elif "greet everyone" in cmd:
        if not camera.is_available() or not camera.is_yolo_available():
            _respond("I can't see anyone to greet.", state.current_language)
        else:
            count = camera.count_people()
            if count == 0:
                response = "There's nobody here to greet. Awkward."
            elif count == 1:
                response = chat.get_response(
                    "Greet one person you see standing in front of you",
                    honesty=state.honesty,
                    humor=state.humor,
                    target_language=state.current_language,
                )
            else:
                response = chat.get_response(
                    f"Greet a group of {count} people standing in front of you",
                    honesty=state.honesty,
                    humor=state.humor,
                    target_language=state.current_language,
                )
            _respond(response, state.current_language)

    # Default — chat with AI
    else:
        response = chat.get_response(
            command,
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)

    return state


def process_controller_command(command, state):
    """Route a controller button press to the appropriate handler.

    Returns the updated state, or "stop" to signal shutdown.
    """
    handlers = {
        "move_forward": lambda: movement.move_forward(state.current_language),
        "turn_left": lambda: movement.turn_left(state.current_language),
        "turn_right": lambda: movement.turn_right(state.current_language),
        "neutral": lambda: movement.neutral(state.current_language),
    }

    if command == "stop":
        response = chat.get_response(
            "Goodbye",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)
        time.sleep(1)
        return "stop"

    handler = handlers.get(command)
    if handler:
        handler()
        response = chat.get_response(
            command.replace("_", " ").title(),
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language)

    return state
