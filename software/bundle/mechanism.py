# TARS Mechanism Control — Servo motor driver
# Now uses shared tars/ package. This file is kept for backward compatibility.

import sys
from pathlib import Path

# Add project root to path so tars/ package can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from tars import config  # noqa: E402
from tars.commands.language import get_movement_message  # noqa: E402, F401
from tars.commands.movement import (  # noqa: E402, F401
    move_forward,
    neutral,
    turn_left,
    turn_right,
)
from tars.hardware.servos import angle_to_pulse, initialize, set_angle  # noqa: E402, F401

# Re-export constants for any code that imports them directly
CHANNEL_TORSO = config.CHANNEL_TORSO
CHANNEL_LEFT_ARM = config.CHANNEL_LEFT_ARM
CHANNEL_RIGHT_ARM = config.CHANNEL_RIGHT_ARM
FORWARD_POS = config.FORWARD_POS
NEUTRAL_POS = config.NEUTRAL_POS
BACKWARD_POS = config.BACKWARD_POS
LEFT_ARM_NEUTRAL_POS = config.LEFT_ARM_NEUTRAL_POS
RIGHT_ARM_NEUTRAL_POS = config.RIGHT_ARM_NEUTRAL_POS

# Alias for backward compatibility
set_servo_angle = set_angle

# Initialize hardware and go to neutral on import (original behavior)
initialize()
neutral()
