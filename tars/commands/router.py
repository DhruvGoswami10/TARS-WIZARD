import time

from tars.ai import chat
from tars.commands import info, language, movement
from tars.hardware import camera
from tars.voice import speaker


def process_command(command, state):
    """Route a voice/text command to the appropriate handler.

    Returns the updated state, or "stop" to signal shutdown.
    """
    if not command:
        return state

    print(f"Received command: {command}")

    # Language switching
    if "speak" in command and any(lang in command for lang in language.get_supported_languages()):
        for lang in language.get_supported_languages():
            if lang in command:
                state.current_language = lang
                response = chat.get_response(
                    "Confirm language change",
                    honesty=state.honesty,
                    humor=state.humor,
                    target_language=state.current_language,
                )
                speaker.speak(response, state.current_language)
                return state

    # Movement commands
    if "move forward" in command or "take 2 steps" in command:
        movement.move_forward(state.current_language)
        response = chat.get_response(
            "Moving forward",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)

    elif "turn left" in command:
        movement.turn_left(state.current_language)
        response = chat.get_response(
            "Turning left",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)

    elif "turn right" in command:
        movement.turn_right(state.current_language)
        response = chat.get_response(
            "Turning right",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)

    # Shutdown
    elif "stop" in command or "exit" in command:
        response = chat.get_response(
            "Goodbye",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)
        time.sleep(1)
        return "stop"

    # Info commands
    elif "time" in command or "date" in command:
        response = info.get_current_time()
        speaker.speak(response, state.current_language)

    elif "weather" in command:
        response = info.get_weather()
        speaker.speak(response, state.current_language)

    # Camera / vision commands
    elif any(phrase in command for phrase in ("what do you see", "look around", "describe")):
        if not camera.is_available():
            speaker.speak("My eyes are offline. No camera detected.", state.current_language)
        else:
            speaker.speak("Let me take a look...", state.current_language)
            response = camera.describe_scene()
            speaker.speak(response, state.current_language)

    elif "how many people" in command:
        if not camera.is_available():
            speaker.speak("I can't see anyone — no camera.", state.current_language)
        elif not camera.is_yolo_available():
            speaker.speak("My detection system is offline. I need ultralytics installed.", state.current_language)
        else:
            count = camera.count_people()
            if count == 0:
                response = "I don't see anyone. Either I'm alone, or everyone's hiding."
            elif count == 1:
                response = "I see one person. Just you and me, I guess."
            else:
                response = f"I count {count} people. That's {count} more than I'd prefer."
            speaker.speak(response, state.current_language)

    elif "greet everyone" in command:
        if not camera.is_available() or not camera.is_yolo_available():
            speaker.speak("I can't see anyone to greet.", state.current_language)
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
            speaker.speak(response, state.current_language)

    # Default — chat with AI
    else:
        response = chat.get_response(
            command,
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        speaker.speak(response, state.current_language)

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
        speaker.speak(response, state.current_language)
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
        speaker.speak(response, state.current_language)

    return state
