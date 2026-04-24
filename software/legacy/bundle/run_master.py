# TARS Bundle Launcher (DEPRECATED)
# This file is kept for backward compatibility.
# Use main.py instead:  python main.py

import sys
from pathlib import Path

print("=" * 50)
print("DEPRECATED: Use 'python main.py' instead.")
print("This launcher will be removed in a future version.")
print("=" * 50)
print()

# Still works for now — launches the old way
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

import threading  # noqa: E402

from software.bundle import controller, voice  # noqa: E402

voice_thread = threading.Thread(target=voice.main)
controller_thread = threading.Thread(target=controller.main)

voice_thread.start()
controller_thread.start()

voice_thread.join()
controller_thread.join()
