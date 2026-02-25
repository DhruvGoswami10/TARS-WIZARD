import time

from tars import config
from tars.commands.language import get_movement_message
from tars.hardware import servos


def move_forward(language="english"):
    """Walk forward — coordinated torso and arm movement."""
    print(get_movement_message("forward", language))
    servos.set_angle(config.CHANNEL_TORSO, config.BACKWARD_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, -130)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, 130)
    time.sleep(config.ARM_DELAY)
    servos.set_angle(config.CHANNEL_TORSO, config.FORWARD_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, config.LEFT_ARM_NEUTRAL_POS)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, config.RIGHT_ARM_NEUTRAL_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_TORSO, config.NEUTRAL_POS)
    time.sleep(config.SETTLE_DELAY)


def turn_left(language="english"):
    """Turn left — torso forward, arms sweep left."""
    print(get_movement_message("left", language))
    servos.set_angle(config.CHANNEL_TORSO, config.FORWARD_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, 130)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, 130)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_TORSO, config.NEUTRAL_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, config.LEFT_ARM_NEUTRAL_POS)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, config.RIGHT_ARM_NEUTRAL_POS)
    time.sleep(config.SETTLE_DELAY)


def turn_right(language="english"):
    """Turn right — torso forward, arms sweep right."""
    print(get_movement_message("right", language))
    servos.set_angle(config.CHANNEL_TORSO, config.FORWARD_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, -130)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, -130)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_TORSO, config.NEUTRAL_POS)
    time.sleep(config.STEP_DELAY)
    servos.set_angle(config.CHANNEL_LEFT_ARM, config.LEFT_ARM_NEUTRAL_POS)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, config.RIGHT_ARM_NEUTRAL_POS)
    time.sleep(config.SETTLE_DELAY)


def neutral(language="english"):
    """Return all servos to neutral position."""
    print(get_movement_message("neutral", language))
    servos.set_angle(config.CHANNEL_TORSO, config.NEUTRAL_POS)
    servos.set_angle(config.CHANNEL_LEFT_ARM, config.LEFT_ARM_NEUTRAL_POS)
    servos.set_angle(config.CHANNEL_RIGHT_ARM, config.RIGHT_ARM_NEUTRAL_POS)
