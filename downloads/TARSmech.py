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

# Helper functions
def angle_to_pulse(angle):
    min_pulse = 1000
    max_pulse = 2000
    pulse_width = min_pulse + (max_pulse - min_pulse) * ((angle + 180) / 360)
    return int(pulse_width * 65535 / 20000)

def set_servo_angle(channel, angle):
    pulse_length = angle_to_pulse(angle)
    pca.channels[channel].duty_cycle = pulse_length
    print(f"Servo on channel {channel} set to {angle}°")

def move_forward():
    print("Moving forward")
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
    
def turn_left():
    print("Turning left")
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, 130)
    set_servo_angle(CHANNEL_RIGHT_ARM, 130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def turn_right():
    print("Turning right")
    set_servo_angle(CHANNEL_TORSO, FORWARD_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, -130)
    set_servo_angle(CHANNEL_RIGHT_ARM, -130)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    time.sleep(0.2)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

def neutral():
    set_servo_angle(CHANNEL_TORSO, NEUTRAL_POS)
    set_servo_angle(CHANNEL_LEFT_ARM, LEFT_ARM_NEUTRAL_POS)
    set_servo_angle(CHANNEL_RIGHT_ARM, RIGHT_ARM_NEUTRAL_POS)

# Map 8BitDo button codes to functions
BUTTON_MAP = {
    305: move_forward,   # 'A' button on 8BitDo
    307: turn_left,      # 'X' button on 8BitDo
    304: turn_right      # 'B' button on 8BitDo
}

# Main event loop
try:
    # Locate the controller device
    gamepad = InputDevice('/dev/input/event15')  # Adjust event number as needed

    print("Listening for controller inputs...")
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_KEY and event.value == 1:  # Key press event
            if event.code == 309:  # 'Y' button to quit
                print("Quitting program")
                break
            elif event.code in BUTTON_MAP:
                BUTTON_MAP[event.code]()  # Call the mapped function
            else:
                print("Unmapped button pressed")

except KeyboardInterrupt:
    print("\nProgram Interrupted")

finally:
    pca.deinit()  # Clean up
    print("Program terminated safely.")
