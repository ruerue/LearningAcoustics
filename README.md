# LearningAcoustics

A simple Python library for acoustic calculations and learning. Designed to be used from smartphones (Pythonista 3) and command-line interfaces.

## Features

- **Decibel Calculations**: Convert between linear values and dB, calculate sound pressure levels
- **Frequency Analysis**: Convert between Hz and wavelength, lookup musical notes
- **Sound Attenuation**: Calculate sound attenuation using inverse square law and atmospheric models

## Installation

### Option 1: From GitHub (Pythonista 3 or Desktop)

```bash
pip install git+https://github.com/ruerue/LearningAcoustics.git
```

### Option 2: Local Installation (Development)

```bash
git clone https://github.com/ruerue/LearningAcoustics.git
cd LearningAcoustics
pip install -e .
```

## Quick Start

### Pythonista 3 (iPhone/iPad) - Short Function Names

The library provides short, easy-to-type function names for quick calculations:

```python
from acoustics import lin2db, db2lin, hz2wave, wave2hz, note_freq, spl

# Decibel calculations
lin2db(10)              # → 20.0 dB
db2lin(20)              # → 10.0

# Frequency/wavelength conversions
hz2wave(440)            # → 0.78 m (wavelength of A4 note)
wave2hz(0.78)           # → 441.67 Hz

# Musical notes
note_freq('A4')         # → 440.0 Hz
note_freq('C4')         # → 261.63 Hz

# Sound pressure level
spl(0.0002)             # → 20.0 dB SPL
```

### Desktop/Script - Full Function Names

For clarity and documentation, you can also use the full function names:

```python
from acoustics import linear_to_db, frequency_to_wavelength, musical_note_frequency

# Same functionality with longer names
linear_to_db(10)                    # → 20.0 dB
frequency_to_wavelength(440)        # → 0.78 m
musical_note_frequency('A4')        # → 440.0 Hz
```

## Available Short Functions

### Decibel (DB) Functions
| Short Name | Full Name | Description |
|-----------|-----------|-------------|
| `lin2db(value)` | `linear_to_db(value)` | Convert linear value to dB |
| `db2lin(db)` | `db_to_linear(db)` | Convert dB to linear value |
| `spl(pressure)` | `sound_pressure_level(pressure)` | Calculate sound pressure level |
| `pow2db(ratio)` | `power_ratio_to_db(ratio)` | Convert power ratio to dB |

### Frequency Functions
| Short Name | Full Name | Description |
|-----------|-----------|-------------|
| `hz2wave(hz)` | `frequency_to_wavelength(hz)` | Convert Hz to wavelength (m) |
| `wave2hz(wavelength)` | `wavelength_to_frequency(wavelength)` | Convert wavelength to Hz |
| `note_freq(note)` | `musical_note_frequency(note)` | Get frequency of a musical note (e.g., 'A4', 'C#4') |
| `find_note(hz)` | `frequency_to_musical_note(hz)` | Find the nearest musical note for a frequency |
| `octup(hz)` | `octave_up(hz)` | Get frequency one octave higher |
| `octdn(hz)` | `octave_down(hz)` | Get frequency one octave lower |

### Attenuation Functions
| Short Name | Full Name | Description |
|-----------|-----------|-------------|
| `inv_square(distance)` | `inverse_square_law(distance)` | Calculate attenuation at distance |
| `atm_atten(freq, distance)` | `atmospheric_attenuation(freq, distance)` | Calculate atmospheric attenuation |
| `comb_atten(distance, freq)` | `combined_attenuation(distance, freq)` | Calculate combined geometric + atmospheric attenuation |

## Command-Line Interface

For terminal use, run:

```bash
python main.py db --linear-to-db 10
python main.py frequency --hz-to-wavelength 440
python main.py attenuation --combined 100 1000
```

See `python main.py --help` for all options.

## Examples

### Example 1: Calculate SPL from pressure
```python
from acoustics import spl

# Sound pressure = 0.0002 Pa
decibel_level = spl(0.0002)
print(f"SPL: {decibel_level:.1f} dB")  # SPL: 20.0 dB
```

### Example 2: Find musical note for a frequency
```python
from acoustics import find_note

note, freq, cents = find_note(435)
print(f"{435} Hz is close to {note} ({freq:.1f} Hz, {cents:+.1f} cents off)")
```

### Example 3: Calculate wavelength for different frequencies
```python
from acoustics import hz2wave

frequencies = [20, 100, 440, 4000, 20000]
for f in frequencies:
    wavelength = hz2wave(f)
    print(f"{f:5} Hz → {wavelength:.3f} m")
```

### Example 4: Attenuation over distance
```python
from acoustics import inv_square

# Source at 100 dB SPL at 1m, what's the SPL at 10m?
spl_at_10m = inv_square(10, reference_distance=1, reference_level=100)
print(f"SPL at 10m: {spl_at_10m:.1f} dB")  # 80.0 dB
```

## Usage in Pythonista 3 (iPhone/iPad)

1. **Install the package** (one-time setup):
   ```python
   import os
   os.system('pip install git+https://github.com/ruerue/LearningAcoustics.git')
   ```

2. **Import and use**:
   ```python
   from acoustics import lin2db, hz2wave, note_freq
   
   # Quick calculations
   print(lin2db(10))           # 20.0
   print(hz2wave(440))         # 0.78
   print(note_freq('A4'))      # 440.0
   ```

3. **In Pythonista 3 REPL**:
   You can type commands directly:
   ```python
   >>> from acoustics import lin2db
   >>> lin2db(10)
   20.0
   ```

## Project Structure

```
LearningAcoustics/
├── acoustics/
│   ├── __init__.py       # Package initialization with short aliases
│   ├── db.py             # Decibel calculations
│   ├── frequency.py      # Frequency analysis
│   └── attenuation.py    # Sound attenuation
├── main.py               # Command-line interface
├── setup.py              # Package setup for pip
└── README.md             # This file
```

## License

MIT License

## Author

Ruerue

## Contributing

Suggestions and improvements are welcome!

## See Also

- [Acoustics on Wikipedia](https://en.wikipedia.org/wiki/Acoustics)
- [Sound Pressure Level (SPL)](https://en.wikipedia.org/wiki/Sound_pressure)
- [Frequency and Wavelength](https://en.wikipedia.org/wiki/Frequency)
