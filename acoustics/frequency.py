"""
Frequency analysis functions for acoustic learning.
"""

import math


# Speed of sound in air at 20°C (m/s)
SPEED_OF_SOUND = 343.0

# Musical notes (A4 = 440 Hz, standard tuning)
MUSICAL_NOTES = {
    'C0': 16.35, 'C#0': 17.32, 'D0': 18.35, 'D#0': 19.45, 'E0': 20.60, 'F0': 21.83,
    'F#0': 23.12, 'G0': 24.50, 'G#0': 25.96, 'A0': 27.50, 'A#0': 29.14, 'B0': 30.87,
    'C1': 32.70, 'C#1': 34.65, 'D1': 36.71, 'D#1': 38.89, 'E1': 41.20, 'F1': 43.65,
    'F#1': 46.25, 'G1': 49.00, 'G#1': 51.91, 'A1': 55.00, 'A#1': 58.27, 'B1': 61.74,
    'C2': 65.41, 'C#2': 69.30, 'D2': 73.42, 'D#2': 77.78, 'E2': 82.41, 'F2': 87.31,
    'F#2': 92.50, 'G2': 98.00, 'G#2': 103.83, 'A2': 110.00, 'A#2': 116.54, 'B2': 123.47,
    'C3': 130.81, 'C#3': 138.59, 'D3': 146.83, 'D#3': 155.56, 'E3': 164.81, 'F3': 174.61,
    'F#3': 185.00, 'G3': 196.00, 'G#3': 207.65, 'A3': 220.00, 'A#3': 233.08, 'B3': 246.94,
    'C4': 261.63, 'C#4': 277.18, 'D4': 293.66, 'D#4': 311.13, 'E4': 329.63, 'F4': 349.23,
    'F#4': 369.99, 'G4': 392.00, 'G#4': 415.30, 'A4': 440.00, 'A#4': 466.16, 'B4': 493.88,
    'C5': 523.25, 'C#5': 554.37, 'D5': 587.33, 'D#5': 622.25, 'E5': 659.25, 'F5': 698.46,
    'F#5': 739.99, 'G5': 783.99, 'G#5': 830.61, 'A5': 880.00, 'A#5': 932.33, 'B5': 987.77,
    'C6': 1046.50, 'C#6': 1108.73, 'D6': 1174.66, 'D#6': 1244.51, 'E6': 1318.51, 'F6': 1396.91,
    'F#6': 1479.98, 'G6': 1567.98, 'G#6': 1661.22, 'A6': 1760.00, 'A#6': 1864.66, 'B6': 1975.53,
    'C7': 2093.00, 'C#7': 2217.46, 'D7': 2349.32, 'D#7': 2489.02, 'E7': 2637.02, 'F7': 2793.83,
    'F#7': 2959.96, 'G7': 3135.96, 'G#7': 3322.44, 'A7': 3520.00, 'A#7': 3729.31, 'B7': 3951.07,
    'C8': 4186.01,
}


def frequency_to_wavelength(frequency, speed_of_sound=SPEED_OF_SOUND):
    """
    Calculate wavelength from frequency.

    Args:
        frequency: Frequency in Hz
        speed_of_sound: Speed of sound in m/s (default: 343 m/s at 20°C)

    Returns:
        Wavelength in meters (m)

    Example:
        >>> frequency_to_wavelength(440)  # A4 note
        0.78
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    if speed_of_sound <= 0:
        raise ValueError("Speed of sound must be positive")
    return speed_of_sound / frequency


def wavelength_to_frequency(wavelength, speed_of_sound=SPEED_OF_SOUND):
    """
    Calculate frequency from wavelength.

    Args:
        wavelength: Wavelength in meters (m)
        speed_of_sound: Speed of sound in m/s (default: 343 m/s at 20°C)

    Returns:
        Frequency in Hz

    Example:
        >>> wavelength_to_frequency(0.78)  # approximately 440 Hz
        440.0
    """
    if wavelength <= 0:
        raise ValueError("Wavelength must be positive")
    if speed_of_sound <= 0:
        raise ValueError("Speed of sound must be positive")
    return speed_of_sound / wavelength


def musical_note_frequency(note):
    """
    Get the frequency of a musical note.

    Args:
        note: Musical note (e.g., 'A4', 'C4', 'C#4')

    Returns:
        Frequency in Hz

    Example:
        >>> musical_note_frequency('A4')
        440.0
        >>> musical_note_frequency('C4')
        261.63
    """
    note = note.upper()
    if note not in MUSICAL_NOTES:
        available_notes = ", ".join(sorted(MUSICAL_NOTES.keys()))
        raise ValueError(f"Unknown note: {note}. Available notes: {available_notes}")
    return MUSICAL_NOTES[note]


def frequency_to_musical_note(frequency, tolerance=2.0):
    """
    Find the nearest musical note for a given frequency.

    Args:
        frequency: Frequency in Hz
        tolerance: Maximum difference in cents (1 semitone = 100 cents)

    Returns:
        Tuple of (note_name, exact_frequency, difference_in_cents)

    Example:
        >>> frequency_to_musical_note(440)
        ('A4', 440.0, 0.0)
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")

    # Find the closest note
    min_diff = float('inf')
    closest_note = None
    closest_freq = None

    for note, freq in MUSICAL_NOTES.items():
        diff = abs(frequency - freq)
        if diff < min_diff:
            min_diff = diff
            closest_note = note
            closest_freq = freq

    # Calculate difference in cents
    cents_diff = 1200 * math.log2(frequency / closest_freq) if closest_freq else 0

    return closest_note, closest_freq, cents_diff


def octave_up(frequency):
    """
    Get the frequency one octave higher.

    Args:
        frequency: Frequency in Hz

    Returns:
        Frequency one octave higher (in Hz)

    Example:
        >>> octave_up(440)
        880.0
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    return frequency * 2


def octave_down(frequency):
    """
    Get the frequency one octave lower.

    Args:
        frequency: Frequency in Hz

    Returns:
        Frequency one octave lower (in Hz)

    Example:
        >>> octave_down(440)
        220.0
    """
    if frequency <= 0:
        raise ValueError("Frequency must be positive")
    return frequency / 2
