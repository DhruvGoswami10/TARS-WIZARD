from openai import OpenAI

from tars import config

# OpenAI client — initialized lazily
_client = None
_openai_available = False


def initialize():
    """Initialize OpenAI client."""
    global _client, _openai_available
    if not config.OPENAI_API_KEY:
        print("WARNING: OpenAI API key not set. AI responses will be limited.")
        return
    _client = OpenAI(api_key=config.OPENAI_API_KEY)
    _openai_available = True
    print("OpenAI client initialized")


def is_available():
    """Check if AI is available."""
    return _openai_available


def get_response(user_input, honesty=0.5, humor=0.5, target_language="english"):
    """Get a TARS-style AI response."""
    if not _openai_available:
        return "My AI brain is offline. Set your OpenAI API key in .env to fix this."

    messages = [
        {
            "role": "system",
            "content": (
                f"You are TARS, the sarcastic robot from Interstellar. "
                f"Respond to user queries with one-liners filled with sarcasm. "
                f"Your honesty level is at {honesty * 100}% and humor level is at {humor * 100}%. "
                f"Respond in {target_language}. Keep the sarcastic tone regardless of language."
            ),
        },
        {"role": "user", "content": user_input},
    ]
    try:
        response = _client.chat.completions.create(
            model=config.AI_MODEL,
            messages=messages,
            max_tokens=config.AI_MAX_TOKENS,
            temperature=config.AI_TEMPERATURE,
            timeout=10,
        )
        content = response.choices[0].message.content.strip()
        return content if content else "Oh, come on, say something meaningful!"
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return "My circuits are fried. Try again in a moment."
