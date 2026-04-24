from tars import config

# Hardware state
_pca = None
_servo_initialized = False


def _init_hardware():
    """Initialize PCA9685 servo controller. Call once at startup."""
    global _pca, _servo_initialized
    try:
        import busio
        from board import SCL, SDA
        from adafruit_pca9685 import PCA9685

        i2c = busio.I2C(SCL, SDA)
        _pca = PCA9685(i2c)
        _pca.frequency = config.SERVO_FREQUENCY
        _servo_initialized = True
        print("Servo controller initialized successfully")
    except ImportError:
        print("Hardware libraries not found. Running in simulation mode.")
    except Exception as e:
        print(f"Error initializing servo controller: {e}")


def is_initialized():
    """Check if servo hardware is available."""
    return _servo_initialized


def angle_to_pulse(angle):
    """Convert angle (-180 to +180) to PCA9685 duty cycle value."""
    pulse_width = config.PULSE_MIN + (config.PULSE_MAX - config.PULSE_MIN) * ((angle + 180) / 360)
    return int(pulse_width * 65535 / 20000)


def set_angle(channel, angle):
    """Set a servo to a specific angle."""
    if not _servo_initialized:
        print(f"[SIM] Servo channel {channel} -> {angle}")
        return
    pulse_length = angle_to_pulse(angle)
    _pca.channels[channel].duty_cycle = pulse_length


def initialize():
    """Initialize hardware and set servos to neutral."""
    _init_hardware()
