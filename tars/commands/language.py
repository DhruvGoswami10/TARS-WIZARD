from tars import config


class LanguageState:
    def __init__(self):
        self.current_language = config.DEFAULT_LANGUAGE
        self.humor = config.DEFAULT_HUMOR / 100.0
        self.honesty = config.DEFAULT_HONESTY / 100.0


def get_voice_id(language):
    """Get AWS Polly voice ID for a language."""
    return config.LANGUAGE_VOICES.get(
        language,
        config.LANGUAGE_VOICES.get("english", "en-US-GuyNeural"),
    )


def get_movement_message(movement_type, language="english"):
    """Get localized movement message."""
    messages = config.MOVEMENT_MESSAGES.get(language, config.MOVEMENT_MESSAGES.get("english", {}))
    return messages.get(movement_type, "Moving")


def get_supported_languages():
    """Return list of supported language names."""
    return list(config.LANGUAGE_VOICES.keys())
