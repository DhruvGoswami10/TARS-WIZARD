import time
from adafruit_pca9685 import PCA9685
from board import SCL, SDA
import busio
from evdev import InputDevice, categorize, ecodes

# Initialize I2C bus and PCA9685
i2c = busio.I2C(SCL, SDA)
pca = PCA9685(i2c)
pca.frequency = 50  # Typical frequency for servos

# Define servo channels and ranges
CHANNEL_TORSO = 0
CHANNEL_LEFT_ARM = 3
CHANNEL_RIGHT_ARM = 4

# Torso and arm positions
UP_HEIGHT = 130
NEUTRAL_HEIGHT = 0
DOWN_HEIGHT = -130
FORWARD_POS = 130
NEUTRAL_POS = 0
BACKWARD_POS = -130
LEFT_ARM_NEUTRAL_POS = -28
RIGHT_ARM_NEUTRAL_POS = 28

# Movement feedback messages in different languages
MOVEMENT_MESSAGES = {
    'english': {
        'forward': "Moving forward",
        'left': "Turning left",
        'right': "Turning right",
        'neutral': "Returning to neutral position"
    },
    'spanish': {
        'forward': "Moviendo hacia adelante",
        'left': "Girando a la izquierda",
        'right': "Girando a la derecha",
        'neutral': "Volviendo a posición neutral"
    },
    # ...add other language mappings as in mechanism.py...
}

def get_movement_message(movement_type, language='english'):
    """Get movement feedback message in specified language"""
    messages = MOVEMENT_MESSAGES.get(language, MOVEMENT_MESSAGES['english'])
    return messages.get(movement_type, "Moving")

# Helper functions
def angle_to_pulse(angle):
    min_pulse = 1000
    max_pulse = 2000
    pulse_width = min_pulse + (max_pulse - max_pulse) * ((angle + 180) / 360)
    return int(pulse_width * 65535 / 20000)

def set_servo_angle(channel, angle):
    pulse_length = angle_to_pulse(angle)
    pca.channels[channel].duty_cycle = pulse_length
    print(f"Servo on channel {channel} set to {angle}°")

def move_forward(language='english'):
    print(get_movement_message('forward', language))
    set_servo_angle(CHANNEL_TORSO, BACKWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, -130)
    set_servo_angle(CHANNEL_RIGHT_ARM, 130)
    time.sleep(0.3)
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    
def turn_left(language='english'):
    print(get_movement_message('left', language))
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, 130)
    set_servo_angle(CHANNEL_RIGHT_ARM, 130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def turn_right(language='english'):
    print(get_movement_message('right', language))
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, -130)
    set_servo_angle(CHANNEL_RIGHT_ARM, -130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def neutral(language='english'):
    print(get_movement_message('neutral', language))
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

# Update button mapping to include language parameter
def create_button_map(language='english'):
    return {
        305: lambda: move_forward(language),
        307: lambda: turn_left(language),
        304: lambda: turn_right(language)
    }

# Main event loop
try:
    current_language = 'english'
    gamepad = InputDevice('/dev/input/event15')
    button_map = create_button_map(current_language)

    print("Listening for controller inputs...")
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:
            if event.code == 309:
                print(get_movement_message('quit', current_language))
                break
            elif event.code in button_map:
                button_map[event.code]()
            else:
                print(get_movement_message('unknown', current_language))

except KeyboardInterrupt:
    print("\nProgram Interrupted")

finally:
    pca.deinit()
    print("Program terminated safely.")
