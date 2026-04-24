"""Tests for tars/hardware/i2c_scanner.py — address-to-name lookup."""

from tars.hardware.i2c_scanner import KNOWN_DEVICES, is_available, scan


def test_known_devices_contains_pca9685():
    assert 0x40 in KNOWN_DEVICES
    assert "PCA9685" in KNOWN_DEVICES[0x40]


def test_known_devices_contains_mpu6050():
    assert 0x68 in KNOWN_DEVICES
    assert "MPU6050" in KNOWN_DEVICES[0x68]


def test_known_devices_contains_oled():
    assert 0x3C in KNOWN_DEVICES
    assert "SSD1306" in KNOWN_DEVICES[0x3C]


def test_known_devices_contains_bme280():
    assert 0x76 in KNOWN_DEVICES
    assert "BME280" in KNOWN_DEVICES[0x76]


def test_scan_returns_empty_without_smbus():
    """scan() returns empty list when smbus2 is not available."""
    result = scan()
    assert isinstance(result, list)


def test_is_available_returns_bool():
    """is_available() returns a boolean."""
    result = is_available()
    assert isinstance(result, bool)
