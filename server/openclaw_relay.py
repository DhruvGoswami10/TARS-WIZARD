#!/usr/bin/env python3
"""OpenClaw Relay Server — runs on your laptop alongside OpenClaw.

Bridges TARS (on Pi) with OpenClaw (on laptop) via Telegram Bot API.

Usage:
    pip install flask
    python server/openclaw_relay.py

TARS sends tasks here via HTTP. This server forwards them to OpenClaw
via Telegram and waits for the reply.

Set these environment variables (or create server/.env):
    TELEGRAM_BOT_TOKEN=your-bot-token
    TELEGRAM_CHAT_ID=your-chat-id
"""

import json
import os
import time
import urllib.parse
import urllib.request
from http.server import HTTPServer, BaseHTTPRequestHandler
from threading import Thread, Lock

# Config — set these or create server/.env
BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "")
CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")

# Track the latest bot reply
_latest_reply = None
_latest_reply_lock = Lock()
_poll_thread = None


def telegram_api(method, params=None, timeout=10):
    """Call Telegram Bot API."""
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(params).encode("utf-8") if params else None
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except Exception as e:
        print(f"  Telegram API error: {e}")
        return None


def send_to_openclaw(text):
    """Send a message to OpenClaw via Telegram."""
    result = telegram_api("sendMessage", {
        "chat_id": CHAT_ID,
        "text": text,
    })
    if result and result.get("ok"):
        return result["result"]["message_id"]
    return None


def poll_for_reply(after_msg_id, timeout=120):
    """Poll Telegram for OpenClaw's reply after our message.

    Uses getUpdates with long polling. Since this relay server is the
    only thing calling getUpdates (OpenClaw uses webhooks or its own
    polling which we temporarily take over), there's no conflict.
    """
    global _latest_reply

    start = time.time()
    last_update_id = 0

    while time.time() - start < timeout:
        result = telegram_api("getUpdates", {
            "offset": last_update_id + 1,
            "timeout": 5,
            "allowed_updates": json.dumps(["message"]),
        }, timeout=15)

        if not result or not result.get("ok"):
            time.sleep(2)
            continue

        for update in result.get("result", []):
            update_id = update.get("update_id", 0)
            last_update_id = max(last_update_id, update_id)

            message = update.get("message", {})
            msg_id = message.get("message_id", 0)
            msg_chat = str(message.get("chat", {}).get("id", ""))
            text = message.get("text", "")
            from_user = message.get("from", {})

            # Skip our own messages (from the bot itself sending)
            if from_user.get("id") == _bot_id:
                continue

            # Found a reply in our chat after our sent message
            if msg_chat == str(CHAT_ID) and text and msg_id > after_msg_id:
                # Confirm processing
                telegram_api("getUpdates", {"offset": last_update_id + 1})
                return text

    return None


# Bot's own ID (to filter out its own messages)
_bot_id = None


class RelayHandler(BaseHTTPRequestHandler):
    """HTTP handler for TARS requests."""

    def do_GET(self):
        if self.path == "/health":
            self._json_response({"status": "ok"})
        else:
            self._json_response({"error": "not found"}, 404)

    def do_POST(self):
        if self.path == "/task":
            content_length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(content_length)

            try:
                data = json.loads(body)
                task = data.get("task", "")
            except (json.JSONDecodeError, KeyError):
                self._json_response({"error": "invalid JSON"}, 400)
                return

            if not task:
                self._json_response({"error": "no task provided"}, 400)
                return

            print(f"\n>> Task from TARS: {task}")

            # Send to OpenClaw via Telegram
            msg_id = send_to_openclaw(task)
            if not msg_id:
                self._json_response({"error": "failed to send to Telegram"}, 500)
                return

            print(f"   Sent to Telegram (msg_id: {msg_id})")
            print(f"   Waiting for OpenClaw reply...")

            # Wait for OpenClaw's reply
            reply = poll_for_reply(msg_id, timeout=120)

            if reply:
                print(f"<< OpenClaw replied: {reply[:100]}...")
                self._json_response({"response": reply})
            else:
                print("!! OpenClaw didn't respond in time")
                self._json_response({
                    "response": "OpenClaw didn't respond in time. Check Telegram."
                })
        else:
            self._json_response({"error": "not found"}, 404)

    def _json_response(self, data, status=200):
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(json.dumps(data).encode("utf-8"))

    def log_message(self, format, *args):
        # Suppress default access logs, we print our own
        pass


def main():
    global _bot_id, BOT_TOKEN, CHAT_ID

    # Try loading from server/.env
    env_path = os.path.join(os.path.dirname(__file__), ".env")
    if os.path.exists(env_path):
        with open(env_path) as f:
            for line in f:
                line = line.strip()
                if "=" in line and not line.startswith("#"):
                    key, value = line.split("=", 1)
                    os.environ[key.strip()] = value.strip()
        BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", BOT_TOKEN)
        CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", CHAT_ID)

    if not BOT_TOKEN or not CHAT_ID:
        print("ERROR: Set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID")
        print("Either as environment variables or in server/.env")
        return

    # Get bot info
    me = telegram_api("getMe")
    if me and me.get("ok"):
        _bot_id = me["result"]["id"]
        bot_name = me["result"].get("username", "unknown")
        print(f"Bot: @{bot_name} (ID: {_bot_id})")
    else:
        print("WARNING: Could not get bot info")

    # Start HTTP server
    port = 8642
    server = HTTPServer(("0.0.0.0", port), RelayHandler)
    print(f"\nOpenClaw Relay Server running on http://0.0.0.0:{port}")
    print(f"TARS should set: OPENCLAW_SERVER_URL=http://<your-laptop-ip>:{port}")
    print(f"\nWaiting for tasks from TARS...\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nShutting down relay server.")
        server.shutdown()


if __name__ == "__main__":
    main()
