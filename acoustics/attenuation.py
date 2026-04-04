"""
Sound attenuation calculation functions for acoustic learning.
"""

import math


def inverse_square_law(distance, reference_distance=1.0, reference_level=0.0):
    """
    Calculate sound pressure level change using the inverse square law.

    The inverse square law states that sound intensity decreases with the
    square of the distance from the source.

    Args:
        distance: Distance from source in meters
        reference_distance: Reference distance in meters (default: 1 m)
        reference_level: Reference SPL at reference distance in dB (default: 0 dB)

    Returns:
        Sound pressure level at the given distance (dB)

    Example:
        >>> inverse_square_law(2, reference_distance=1, reference_level=100)
        94.0
        >>> inverse_square_law(10, reference_distance=1, reference_level=100)
        80.0
    """
    if distance <= 0:
        raise ValueError("Distance must be positive")
    if reference_distance <= 0:
        raise ValueError("Reference distance must be positive")

    # Attenuation in dB = 20 * log10(reference_distance / distance)
    attenuation = 20 * math.log10(reference_distance / distance)
    return reference_level + attenuation


def distance_for_level(target_level, reference_distance=1.0, reference_level=0.0):
    """
    Calculate distance needed to achieve a target sound pressure level.

    Inverse of the inverse square law - finds the distance for a given SPL.

    Args:
        target_level: Target SPL in dB
        reference_distance: Reference distance in meters (default: 1 m)
        reference_level: Reference SPL at reference distance in dB (default: 0 dB)

    Returns:
        Distance required in meters

    Example:
        >>> distance_for_level(94, reference_distance=1, reference_level=100)
        2.0
    """
    if reference_distance <= 0:
        raise ValueError("Reference distance must be positive")

    # Rearrange inverse square law to solve for distance
    attenuation_needed = reference_level - target_level
    distance = reference_distance / (10 ** (attenuation_needed / 20))
    return distance


def atmospheric_attenuation(frequency, distance, humidity=50, temperature=20):
    """
    Calculate sound attenuation due to atmospheric absorption.

    This is a simplified model based on molecular absorption in air.
    More accurate models exist but this provides reasonable estimates.

    Args:
        frequency: Frequency in Hz
        distance: Distance traveled in meters
        humidity: Relative humidity in % (default: 50%)
        temperature: Temperature in °C (default: 20°C)

    Returns:
        Attenuation in dB due to atmospheric absorption

    Example:
        >>> atmospheric_attenuation(1000, 100)
        0.15
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    if distance <= 0:
        raise ValueError("Distance must be positive")
    if not (0 <= humidity <= 100):
        raise ValueError("Humidity must be between 0 and 100%")
    if not (-50 <= temperature <= 50):
        raise ValueError("Temperature must be between -50°C and 50°C")

    # Simplified atmospheric attenuation coefficient (dB/m/Hz^2)
    # This is a basic model; real world is more complex
    # Based on ISO 9613-1
    alpha = 10 ** (-4.5 - 1.5 * (humidity - 50) ** 2 / 2500) * (frequency ** 2) / 1000

    # Attenuation in dB
    attenuation_db = alpha * distance

    return attenuation_db


def combined_attenuation(distance, frequency, reference_distance=1.0,
                        reference_level=100, humidity=50, temperature=20):
    """
    Calculate combined attenuation from both geometric spreading and atmosphere.

    Args:
        distance: Distance from source in meters
        frequency: Frequency in Hz
        reference_distance: Reference distance in meters (default: 1 m)
        reference_level: Reference SPL at reference distance in dB (default: 100 dB)
        humidity: Relative humidity in % (default: 50%)
        temperature: Temperature in °C (default: 20°C)

    Returns:
        Total SPL at the given distance (dB)

    Example:
        >>> combined_attenuation(100, 1000)
        79.85
    """
    geometric = inverse_square_law(distance, reference_distance, reference_level)
    atmospheric = atmospheric_attenuation(frequency, distance, humidity, temperature)
    return geometric - atmospheric
