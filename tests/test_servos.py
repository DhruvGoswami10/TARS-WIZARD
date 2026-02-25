"""Tests for tars/hardware/servos.py — pulse calculation and sim mode."""

from tars.hardware.servos import angle_to_pulse


def test_angle_to_pulse_center():
    """Angle 0 should produce the midpoint pulse."""
    pulse = angle_to_pulse(0)
    # midpoint pulse_width = 1000 + (2000-1000) * (180/360) = 1500
    expected = int(1500 * 65535 / 20000)
    assert pulse == expected


def test_angle_to_pulse_min():
    """Angle -180 should produce minimum pulse."""
    pulse = angle_to_pulse(-180)
    # pulse_width = 1000 + (2000-1000) * (0/360) = 1000
    expected = int(1000 * 65535 / 20000)
    assert pulse == expected


def test_angle_to_pulse_max():
    """Angle +180 should produce maximum pulse."""
    pulse = angle_to_pulse(180)
    # pulse_width = 1000 + (2000-1000) * (360/360) = 2000
    expected = int(2000 * 65535 / 20000)
    assert pulse == expected


def test_angle_to_pulse_positive():
    """Positive angle gives a pulse above midpoint."""
    assert angle_to_pulse(90) > angle_to_pulse(0)


def test_angle_to_pulse_negative():
    """Negative angle gives a pulse below midpoint."""
    assert angle_to_pulse(-90) < angle_to_pulse(0)


def test_angle_to_pulse_monotonic():
    """Pulse increases monotonically with angle."""
    pulses = [angle_to_pulse(a) for a in range(-180, 181, 10)]
    for i in range(len(pulses) - 1):
        assert pulses[i] <= pulses[i + 1]
