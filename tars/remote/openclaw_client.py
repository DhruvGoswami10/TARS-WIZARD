"""OpenClaw integration via Telegram Bot API.

Sends tasks to OpenClaw (running on laptop) through its Telegram bot.
Polls for the response and returns it to TARS.

Flow:
    1. TARS sends a message to the Telegram bot
    2. OpenClaw receives it, executes browser task
    3. OpenClaw replies in Telegram
    4. TARS polls for the reply and speaks it
"""

import time
import urllib.error
import urllib.parse
import urllib.request
import json

from tars import config

_bot_token = None
_chat_id = None
_available = False


def initialize():
    """Initialize the OpenClaw Telegram client."""
    global _bot_token, _chat_id, _available

    _bot_token = config.env("TELEGRAM_BOT_TOKEN", "")
    _chat_id = config.env("TELEGRAM_CHAT_ID", "")

    if _bot_token and _chat_id:
        _available = True
        print("OpenClaw client initialized (Telegram)")
    else:
        print("OpenClaw not configured (set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID in .env)")


def is_available():
    """Check if OpenClaw is configured."""
    return _available


def _telegram_api(method, params=None):
    """Call the Telegram Bot API."""
    url = f"https://api.telegram.org/bot{_bot_token}/{method}"
    if params:
        data = urllib.parse.urlencode(params).encode("utf-8")
    else:
        data = None

    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"Telegram API error: {e}")
        return None


def _get_latest_message_id():
    """Get the ID of the latest message in the chat (to know where to start polling)."""
    result = _telegram_api("getUpdates", {"chat_id": _chat_id, "offset": -1})
    if result and result.get("ok") and result.get("result"):
        return result["result"][-1].get("update_id", 0)
    return 0


def send_task(task_text, timeout=90):
    """Send a task to OpenClaw and wait for its response.

    Args:
        task_text: The task to send (e.g., "find flights to Dubai")
        timeout: Max seconds to wait for a response (default 90)

    Returns:
        OpenClaw's response text, or an error message.
    """
    if not _available:
        return "OpenClaw is not configured. Add TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID to .env."

    # Get current latest update ID so we only look at NEW messages
    last_update_id = _get_latest_message_id()

    # Send the task message to the bot
    send_result = _telegram_api("sendMessage", {
        "chat_id": _chat_id,
        "text": task_text,
    })

    if not send_result or not send_result.get("ok"):
        return "Failed to send task to OpenClaw."

    sent_message_id = send_result.get("result", {}).get("message_id", 0)

    # Poll for OpenClaw's response
    start_time = time.time()
    poll_interval = 2  # seconds between polls

    while time.time() - start_time < timeout:
        time.sleep(poll_interval)

        updates = _telegram_api("getUpdates", {
            "offset": last_update_id + 1,
            "timeout": 5,
        })

        if not updates or not updates.get("ok"):
            continue

        for update in updates.get("result", []):
            update_id = update.get("update_id", 0)
            message = update.get("message", {})
            msg_chat_id = str(message.get("chat", {}).get("id", ""))
            msg_id = message.get("message_id", 0)
            text = message.get("text", "")

            # Skip our own sent message
            if msg_id == sent_message_id:
                last_update_id = max(last_update_id, update_id)
                continue

            # Look for a reply from the bot in our chat
            if msg_chat_id == str(_chat_id) and text and msg_id > sent_message_id:
                # Mark this update as processed
                _telegram_api("getUpdates", {"offset": update_id + 1})
                return text

            last_update_id = max(last_update_id, update_id)

    return "OpenClaw didn't respond in time. It might still be working — check Telegram."
