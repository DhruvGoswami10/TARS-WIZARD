import time

from tars.ai import chat
from tars.commands import info, language, movement, settings
from tars.hardware import camera
from tars.remote import openclaw_client
from tars.ui import terminal
from tars.voice import speaker


def _is_web_task(cmd):
    """Check if the command is a web task for OpenClaw."""
    web_phrases = (
        "search for", "find me", "find flights", "find hotels",
        "look up", "book a", "book me", "check flights",
        "check hotels", "browse", "go to", "open website",
        "search the web", "google", "look online",
        "compare prices", "find restaurants", "find tickets",
        "order", "buy", "purchase", "shop for",
    )
    return any(phrase in cmd for phrase in web_phrases)


def _is_vision_command(cmd):
    """Check if the command is asking TARS to use the camera."""
    vision_phrases = (
        "what do you see", "what can you see", "look around", "describe",
        "what am i holding", "what is this", "what's this", "what is that",
        "what's that", "can you see", "do you see", "take a look",
        "look at this", "look at that", "what's in front",
        "what am i wearing", "read this", "read that",
        "show me", "identify", "recognize",
    )
    return any(phrase in cmd for phrase in vision_phrases)


def _respond(text, lang, text_only=False):
    """Print response to terminal and speak it (unless text-only mode).

    Speech is always non-blocking — plays in background so the voice
    pipeline can immediately start listening for the next command.
    """
    terminal.print_tars(text)
    if not text_only:
        try:
            speaker.speak(text, lang, blocking=False)
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
                _respond(response, state.current_language, state.text_only)
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
        _respond(response, state.current_language, state.text_only)

    elif "turn left" in cmd:
        movement.turn_left(state.current_language)
        response = chat.get_response(
            "Turning left",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language, state.text_only)

    elif "turn right" in cmd:
        movement.turn_right(state.current_language)
        response = chat.get_response(
            "Turning right",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language, state.text_only)

    # Shutdown
    elif "stop" in cmd or cmd in ("exit", "quit"):
        response = chat.get_response(
            "Goodbye",
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language, state.text_only)
        time.sleep(1)
        return "stop"

    # Info commands
    elif "time" in cmd or "date" in cmd:
        response = info.get_current_time()
        _respond(response, state.current_language, state.text_only)

    elif "weather" in cmd:
        response = info.get_weather()
        _respond(response, state.current_language, state.text_only)

    # Settings commands
    elif "set humor" in cmd or "humor to" in cmd:
        response = settings.set_humor(cmd, state)
        _respond(response, state.current_language, state.text_only)

    elif "set honesty" in cmd or "honesty to" in cmd:
        response = settings.set_honesty(cmd, state)
        _respond(response, state.current_language, state.text_only)

    # Camera / vision commands
    elif _is_vision_command(cmd):
        if not camera.is_available():
            _respond("My eyes are offline. No camera detected.", state.current_language, state.text_only)
        else:
            _respond("Let me take a look...", state.current_language, state.text_only)
            response = camera.describe_scene()
            _respond(response, state.current_language, state.text_only)

    elif "how many people" in cmd:
        if not camera.is_available():
            _respond("I can't see anyone — no camera.", state.current_language, state.text_only)
        elif not camera.is_yolo_available():
            msg = "My detection system is offline. I need ultralytics installed."
            _respond(msg, state.current_language, state.text_only)
        else:
            count = camera.count_people()
            if count == 0:
                response = "I don't see anyone. Either I'm alone, or everyone's hiding."
            elif count == 1:
                response = "I see one person. Just you and me, I guess."
            else:
                response = f"I count {count} people. That's {count} more than I'd prefer."
            _respond(response, state.current_language, state.text_only)

    elif "greet everyone" in cmd:
        if not camera.is_available() or not camera.is_yolo_available():
            _respond("I can't see anyone to greet.", state.current_language, state.text_only)
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
            _respond(response, state.current_language, state.text_only)

    # OpenClaw / web tasks
    elif _is_web_task(cmd):
        if not openclaw_client.is_available():
            _respond("My remote agent isn't connected. Set up OpenClaw in .env.",
                     state.current_language, state.text_only)
        else:
            _respond("Let me look that up, give me a moment...",
                     state.current_language, state.text_only)
            result = openclaw_client.send_task(command)
            # Summarize long responses with AI
            if len(result) > 300:
                summary = chat.get_response(
                    f"Summarize this concisely for speaking aloud: {result}",
                    honesty=state.honesty,
                    humor=state.humor,
                    target_language=state.current_language,
                )
                _respond(summary or result, state.current_language, state.text_only)
            else:
                _respond(result, state.current_language, state.text_only)

    # Default — chat with AI
    else:
        response = chat.get_response(
            command,
            honesty=state.honesty,
            humor=state.humor,
            target_language=state.current_language,
        )
        _respond(response, state.current_language, state.text_only)

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
        _respond(response, state.current_language, state.text_only)
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
        _respond(response, state.current_language, state.text_only)

    return state
