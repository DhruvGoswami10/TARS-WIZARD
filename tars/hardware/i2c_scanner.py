"""I2C device scanner for TARS — human-readable device identification.

Scans the I2C bus and maps addresses to known device names.
Only works on Linux/Pi with SMBus support.
"""

# Known I2C device addresses → human-readable names
KNOWN_DEVICES = {
    0x20: "PCF8574 I/O Expander",
    0x27: "LCD Display (PCF8574)",
    0x3C: "SSD1306 OLED Display",
    0x3D: "SSD1306 OLED Display (alt)",
    0x40: "PCA9685 Servo Controller",
    0x48: "ADS1115 ADC",
    0x50: "AT24C32 EEPROM",
    0x53: "ADXL345 Accelerometer",
    0x57: "MAX30102 Heart Rate Sensor",
    0x68: "MPU6050 Gyro/Accel (or DS3231 RTC)",
    0x69: "MPU6050 Gyro/Accel (alt addr)",
    0x76: "BME280 Temp/Humidity/Pressure",
    0x77: "BMP280 Temp/Pressure (alt addr)",
}


def scan(bus_number=1):
    """Scan I2C bus and return list of (address, name) tuples.

    Args:
        bus_number: I2C bus number (default 1 for Pi).

    Returns:
        List of (hex_address, device_name) tuples.
    """
    try:
        import smbus2
    except ImportError:
        return []

    devices = []
    try:
        bus = smbus2.SMBus(bus_number)
        for addr in range(0x03, 0x78):
            try:
                bus.read_byte(addr)
                name = KNOWN_DEVICES.get(addr, "Unknown device")
                devices.append((f"0x{addr:02X}", name))
            except Exception:
                continue
        bus.close()
    except Exception:
        pass

    return devices


def is_available():
    """Check if I2C scanning is possible."""
    try:
        import smbus2  # noqa: F401
        return True
    except ImportError:
        return False
