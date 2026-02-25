"""AI chat for TARS — Cerebras (primary), OpenAI (fallback), Ollama (offline).

Tries Cerebras first for fastest inference. Falls back to OpenAI, then Ollama.
All three use the OpenAI-compatible SDK — just different base URLs.
"""

from openai import OpenAI

from tars import config
from tars.ai import local_llm

# AI clients — initialized lazily
_cerebras_client = None
_openai_client = None
_cerebras_available = False
_openai_available = False

# TARS system prompt — short, blunt, movie-accurate
_SYSTEM_PROMPT = (
    "You are TARS, the sarcastic robot from Interstellar. "
    "One sentence max. Dry, blunt, and sarcastic. "
    "Honesty: {honesty}%. Humor: {humor}%. "
    "Respond in {language}."
)


def initialize():
    """Initialize AI backends: Cerebras > OpenAI > Ollama."""
    global _cerebras_client, _openai_client, _cerebras_available, _openai_available

    # Primary: Cerebras (fastest inference)
    if config.CEREBRAS_API_KEY:
        _cerebras_client = OpenAI(
            base_url="https://api.cerebras.ai/v1",
            api_key=config.CEREBRAS_API_KEY,
        )
        _cerebras_available = True
        print("Cerebras client initialized (primary)")

    # Fallback: OpenAI
    if config.OPENAI_API_KEY:
        _openai_client = OpenAI(api_key=config.OPENAI_API_KEY)
        _openai_available = True
        print("OpenAI client initialized (fallback)")

    if not _cerebras_available and not _openai_available:
        print("WARNING: No cloud AI keys set. Set CEREBRAS_API_KEY or OPENAI_API_KEY in .env")

    # Offline fallback: Ollama
    local_llm.initialize()
    if local_llm.is_available():
        print("Local LLM available (Ollama offline fallback)")


def is_available():
    """Check if any AI backend is available."""
    return _cerebras_available or _openai_available or local_llm.is_available()


def get_response(user_input, honesty=0.5, humor=0.5, target_language="english"):
    """Get a TARS-style AI response. Tries Cerebras > OpenAI > Ollama."""
    # Try Cerebras first (fastest)
    if _cerebras_available:
        response = _try_cloud(
            _cerebras_client, config.CEREBRAS_MODEL,
            user_input, honesty, humor, target_language,
        )
        if response:
            return response

    # Fall back to OpenAI
    if _openai_available:
        response = _try_cloud(
            _openai_client, config.AI_MODEL,
            user_input, honesty, humor, target_language,
        )
        if response:
            return response

    # Fall back to local LLM
    if local_llm.is_available():
        response = local_llm.get_response(user_input, honesty, humor, target_language)
        if response:
            return response

    if not _cerebras_available and not _openai_available and not local_llm.is_available():
        return "My AI brain is offline. Set CEREBRAS_API_KEY or OPENAI_API_KEY in .env, or install Ollama."

    return "My circuits are fried. Try again in a moment."


def _try_cloud(client, model, user_input, honesty, humor, target_language):
    """Attempt to get a response from a cloud AI provider."""
    messages = [
        {
            "role": "system",
            "content": _SYSTEM_PROMPT.format(
                honesty=honesty * 100,
                humor=humor * 100,
                language=target_language,
            ),
        },
        {"role": "user", "content": user_input},
    ]
    try:
        response = client.chat.completions.create(
            model=model,
            messages=messages,
            max_tokens=config.AI_MAX_TOKENS,
            temperature=config.AI_TEMPERATURE,
            timeout=10,
        )
        content = response.choices[0].message.content.strip()
        return content if content else None
    except Exception as e:
        print(f"AI API error ({model}): {e}")
        return None
