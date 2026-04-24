# TARS Voice Assistant — Speech recognition + AI conversation + TTS
# Now uses shared tars/ package. This file is kept for backward compatibility.

import sys
import time
from pathlib import Path

# Add project root to path so tars/ package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tars.ai import chat  # noqa: E402
from tars.commands.language import LanguageState  # noqa: E402
from tars.commands.router import process_command  # noqa: E402
from tars.voice import listener, speaker  # noqa: E402


def main():
    # Initialize subsystems
    speaker.initialize()
    chat.initialize()

    state = LanguageState()
    while True:
        command = listener.listen()
        if command:
            result = process_command(command, state)
            if result == "stop":
                sys.exit()
            state = result
            time.sleep(1)


if __name__ == "__main__":
    main()
