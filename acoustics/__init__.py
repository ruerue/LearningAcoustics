"""
LearningAcoustics: A Python library for acoustic calculations and learning.

This module provides functions for:
- Decibel (dB) calculations
- Frequency analysis
- Sound attenuation calculations
"""

from .db import linear_to_db, db_to_linear, sound_pressure_level, power_ratio_to_db, db_add
from .frequency import (frequency_to_wavelength, wavelength_to_frequency,
                        musical_note_frequency, frequency_to_musical_note,
                        octave_up, octave_down)
from .attenuation import inverse_square_law, atmospheric_attenuation, combined_attenuation

__version__ = "0.1.0"

# ============================================================================
# Full function names (for clarity)
# ============================================================================
__all__ = [
    # DB functions
    "linear_to_db",
    "db_to_linear",
    "sound_pressure_level",
    "power_ratio_to_db",
    "db_add",
    # Frequency functions
    "frequency_to_wavelength",
    "wavelength_to_frequency",
    "musical_note_frequency",
    "frequency_to_musical_note",
    "octave_up",
    "octave_down",
    # Attenuation functions
    "inverse_square_law",
    "atmospheric_attenuation",
    "combined_attenuation",
]

# ============================================================================
# Short function aliases for quick access (Pythonista 3 friendly)
# ============================================================================

# DB functions - short names
lin2db = linear_to_db
db2lin = db_to_linear
spl = sound_pressure_level
pow2db = power_ratio_to_db

# Frequency functions - short names
hz2wave = frequency_to_wavelength
wave2hz = wavelength_to_frequency
note_freq = musical_note_frequency
find_note = frequency_to_musical_note
octup = octave_up
octdn = octave_down

# Attenuation functions - short names
inv_square = inverse_square_law
atm_atten = atmospheric_attenuation
comb_atten = combined_attenuation

# Add short names to __all__
__all__.extend([
    # Short DB function names
    "lin2db",
    "db2lin",
    "spl",
    "pow2db",
    # Short frequency function names
    "hz2wave",
    "wave2hz",
    "note_freq",
    "find_note",
    "octup",
    "octdn",
    # Short attenuation function names
    "inv_square",
    "atm_atten",
    "comb_atten",
])
