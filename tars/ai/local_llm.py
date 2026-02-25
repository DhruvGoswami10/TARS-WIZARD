"""Local LLM fallback via Ollama — works offline when internet is unavailable.

Requires Ollama running locally: https://ollama.ai
Default model: phi3 (small, fast, runs on Pi 5 with 8GB RAM)
"""

import requests

from tars import config

_ollama_available = False
_base_url = "http://localhost:11434"
_model = "phi3"


def initialize():
    """Check if Ollama is running and the model is available."""
    global _ollama_available, _base_url, _model

    _base_url = config.get("local_llm.base_url", "http://localhost:11434")
    _model = config.get("local_llm.model", "phi3")

    try:
        resp = requests.get(f"{_base_url}/api/tags", timeout=2)
        if resp.status_code == 200:
            models = [m["name"] for m in resp.json().get("models", [])]
            # Check if our model (or a variant like "phi3:latest") is available
            if any(_model in m for m in models):
                _ollama_available = True
                return
            print(f"Ollama running but model '{_model}' not found. "
                  f"Run: ollama pull {_model}")
        else:
            print("Ollama not responding.")
    except requests.ConnectionError:
        pass
    except Exception as e:
        print(f"Ollama check failed: {e}")


def is_available():
    """Check if local LLM is available."""
    return _ollama_available


def get_response(user_input, honesty=0.5, humor=0.5, target_language="english"):
    """Get a response from the local LLM via Ollama."""
    if not _ollama_available:
        return None

    system_prompt = (
        f"You are TARS, the sarcastic robot from Interstellar. "
        f"Respond with one-liners filled with sarcasm. "
        f"Honesty: {honesty * 100}%, humor: {humor * 100}%. "
        f"Respond in {target_language}. Keep responses short (1-2 sentences)."
    )

    try:
        resp = requests.post(
            f"{_base_url}/api/chat",
            json={
                "model": _model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input},
                ],
                "stream": False,
                "options": {"num_predict": 100},
            },
            timeout=30,
        )
        if resp.status_code == 200:
            content = resp.json().get("message", {}).get("content", "").strip()
            return content if content else None
    except Exception as e:
        print(f"Local LLM error: {e}")
    return None
