"""AI chat for TARS — GPT-4o-mini with local LLM fallback.

Tries OpenAI first. On network error, falls back to Ollama (if available).
"""

from openai import OpenAI

from tars import config
from tars.ai import local_llm

# OpenAI client — initialized lazily
_client = None
_openai_available = False


def initialize():
    """Initialize OpenAI client and local LLM fallback."""
    global _client, _openai_available
    if not config.OPENAI_API_KEY:
        print("WARNING: OpenAI API key not set. AI responses will be limited.")
    else:
        _client = OpenAI(api_key=config.OPENAI_API_KEY)
        _openai_available = True

    # Always try to initialize local LLM as fallback
    local_llm.initialize()

    if _openai_available:
        print("OpenAI client initialized")
    if local_llm.is_available():
        print("Local LLM available (Ollama fallback)")


def is_available():
    """Check if any AI backend is available."""
    return _openai_available or local_llm.is_available()


def get_response(user_input, honesty=0.5, humor=0.5, target_language="english"):
    """Get a TARS-style AI response. Falls back to local LLM on failure."""
    # Try OpenAI first
    if _openai_available:
        response = _try_openai(user_input, honesty, humor, target_language)
        if response:
            return response

    # Fall back to local LLM
    if local_llm.is_available():
        response = local_llm.get_response(user_input, honesty, humor, target_language)
        if response:
            return response

    if not _openai_available and not local_llm.is_available():
        return "My AI brain is offline. Set your OpenAI API key in .env or install Ollama."

    return "My circuits are fried. Try again in a moment."


def _try_openai(user_input, honesty, humor, target_language):
    """Attempt to get a response from OpenAI."""
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
        return content if content else None
    except Exception as e:
        print(f"OpenAI API error: {e}")
        return None
