"""OpenClaw integration — connects to a relay server on your laptop.

Architecture:
    Pi (TARS) → HTTP → Laptop (relay server) → Telegram → OpenClaw
    Pi (TARS) ← HTTP ← Laptop (relay server) ← Telegram ← OpenClaw

The relay server (server/openclaw_relay.py) runs on your laptop alongside
OpenClaw. It forwards tasks to OpenClaw via Telegram and captures replies.
TARS just makes simple HTTP calls — no Telegram API conflicts.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

from tars import config

_server_url = None
_available = False


def initialize():
    """Initialize the OpenClaw client."""
    global _server_url, _available

    _server_url = config.env("OPENCLAW_SERVER_URL", "")

    if _server_url:
        # Check if server is reachable
        try:
            req = urllib.request.Request(f"{_server_url}/health")
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                if data.get("status") == "ok":
                    _available = True
                    print(f"OpenClaw relay connected ({_server_url})")
                    return
        except Exception:
            pass
        print(f"OpenClaw relay not reachable ({_server_url})")
    else:
        print("OpenClaw not configured (set OPENCLAW_SERVER_URL in .env)")


def is_available():
    """Check if OpenClaw relay server is reachable."""
    return _available


def send_task(task_text, timeout=120):
    """Send a task to OpenClaw via the relay server and get the response.

    The relay server handles all Telegram communication.
    TARS just sends a simple HTTP POST and gets the result back.

    Args:
        task_text: The task to send (e.g., "find flights to Dubai")
        timeout: Max seconds to wait for response

    Returns:
        OpenClaw's response text, or an error message.
    """
    if not _available:
        return "OpenClaw relay is not running. Start server/openclaw_relay.py on your laptop."

    try:
        data = json.dumps({"task": task_text}).encode("utf-8")
        req = urllib.request.Request(
            f"{_server_url}/task",
            data=data,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            result = json.loads(resp.read().decode("utf-8"))
            return result.get("response", "No response from OpenClaw.")
    except urllib.error.URLError as e:
        return f"Can't reach OpenClaw relay: {e}"
    except Exception as e:
        return f"OpenClaw error: {e}"
