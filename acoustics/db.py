"""
Decibel (dB) calculation functions for acoustic learning.
"""

import math


def linear_to_db(value, reference=1.0):
    """
    Convert a linear value to decibels (dB).

    Args:
        value: Linear value to convert
        reference: Reference value (default: 1.0)

    Returns:
        Decibel value (dB)

    Example:
        >>> linear_to_db(10)
        20.0
    """
    if value <= 0:
        raise ValueError("Value must be positive")
    if reference <= 0:
        raise ValueError("Reference must be positive")
    return 20 * math.log10(value / reference)


def db_to_linear(db_value, reference=1.0):
    """
    Convert decibels (dB) to a linear value.

    Args:
        db_value: Decibel value to convert
        reference: Reference value (default: 1.0)

    Returns:
        Linear value

    Example:
        >>> db_to_linear(20)
        10.0
    """
    return reference * (10 ** (db_value / 20))


def sound_pressure_level(pressure, reference=20e-6):
    """
    Calculate Sound Pressure Level (SPL) in dB.

    Args:
        pressure: Sound pressure in pascals (Pa)
        reference: Reference pressure (default: 20 µPa = 20e-6 Pa)

    Returns:
        Sound Pressure Level in dB

    Example:
        >>> sound_pressure_level(20e-6)  # Reference pressure
        0.0
        >>> sound_pressure_level(0.0002)  # 10 Pa
        94.0
    """
    if pressure < 0:
        raise ValueError("Pressure must be non-negative")
    if pressure == 0:
        return float('-inf')
    return 20 * math.log10(pressure / reference)


def power_ratio_to_db(power_ratio):
    """
    Convert power ratio to decibels (dB).

    Args:
        power_ratio: Ratio of powers (P1/P2)

    Returns:
        Power ratio in dB

    Example:
        >>> power_ratio_to_db(10)
        10.0
        >>> power_ratio_to_db(100)
        20.0
    """
    if power_ratio <= 0:
        raise ValueError("Power ratio must be positive")
    return 10 * math.log10(power_ratio)


def db_add(db1, db2):
    """
    Add two dB values (logarithmic addition).

    Args:
        db1: First dB value
        db2: Second dB value

    Returns:
        Sum of dB values (in linear domain, converted back to dB)

    Example:
        >>> db_add(3, 3)
        6.02
    """
    linear_sum = 10 ** (db1 / 10) + 10 ** (db2 / 10)
    return 10 * math.log10(linear_sum)
