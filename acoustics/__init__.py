"""
LearningAcoustics: A Python library for acoustic calculations and learning.

This module provides functions for:
- Decibel (dB) calculations
- Frequency analysis
- Sound attenuation calculations
"""

from .db import linear_to_db, db_to_linear, sound_pressure_level, power_ratio_to_db
from .frequency import frequency_to_wavelength, wavelength_to_frequency, musical_note_frequency
from .attenuation import inverse_square_law, atmospheric_attenuation

__version__ = "0.1.0"

__all__ = [
    # DB functions
    "linear_to_db",
    "db_to_linear",
    "sound_pressure_level",
    "power_ratio_to_db",
    # Frequency functions
    "frequency_to_wavelength",
    "wavelength_to_frequency",
    "musical_note_frequency",
    # Attenuation functions
    "inverse_square_law",
    "atmospheric_attenuation",
]
