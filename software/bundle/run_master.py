# TARS Bundle Launcher — Starts voice + controller threads for headless Pi mode
# Now uses shared tars/ package. This file is kept for backward compatibility.

import sys
import threading
from pathlib import Path

# Add project root to path so tars/ package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from software.bundle import voice, controller  # noqa: E402

voice_thread = threading.Thread(target=voice.main)
controller_thread = threading.Thread(target=controller.main)

voice_thread.start()
controller_thread.start()

voice_thread.join()
controller_thread.join()
