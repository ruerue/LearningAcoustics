#!/usr/bin/env python3
"""
LearningAcoustics CLI - Command-line interface for acoustic calculations.

Usage examples:
    python main.py db --linear-to-db 10
    python main.py db --db-to-linear 20
    python main.py db --spl 0.0002
    python main.py frequency --hz-to-wavelength 440
    python main.py frequency --wavelength-to-hz 0.78
    python main.py frequency --note A4
    python main.py attenuation --inverse-square 100
    python main.py attenuation --combined 100 1000
"""

import argparse
import sys
from acoustics import db, frequency, attenuation


def setup_parser():
    """Set up the argument parser with subcommands."""
    parser = argparse.ArgumentParser(
        description="LearningAcoustics - Acoustic calculations from the command line",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py db --linear-to-db 10
  python main.py frequency --hz-to-wavelength 440
  python main.py attenuation --inverse-square 100
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # DB subcommand
    db_parser = subparsers.add_parser('db', help='Decibel calculations')
    db_group = db_parser.add_mutually_exclusive_group(required=True)
    db_group.add_argument('--linear-to-db', type=float, metavar='VALUE',
                         help='Convert linear value to dB')
    db_group.add_argument('--db-to-linear', type=float, metavar='DB',
                         help='Convert dB to linear value')
    db_group.add_argument('--spl', type=float, metavar='PRESSURE',
                         help='Calculate Sound Pressure Level (Pa)')
    db_group.add_argument('--power-ratio', type=float, metavar='RATIO',
                         help='Convert power ratio to dB')
    db_group.add_argument('--add-db', type=float, nargs=2, metavar=('DB1', 'DB2'),
                         help='Add two dB values')
    db_parser.add_argument('--reference', type=float, default=1.0,
                          help='Reference value (default: 1.0)')

    # Frequency subcommand
    freq_parser = subparsers.add_parser('frequency', help='Frequency calculations')
    freq_group = freq_parser.add_mutually_exclusive_group(required=True)
    freq_group.add_argument('--hz-to-wavelength', type=float, metavar='HZ',
                           help='Convert Hz to wavelength (m)')
    freq_group.add_argument('--wavelength-to-hz', type=float, metavar='WAVELENGTH',
                           help='Convert wavelength (m) to Hz')
    freq_group.add_argument('--note', type=str, metavar='NOTE',
                           help='Get frequency of a musical note (e.g., A4, C#4)')
    freq_group.add_argument('--find-note', type=float, metavar='HZ',
                           help='Find the nearest musical note for a frequency')
    freq_group.add_argument('--octave-up', type=float, metavar='HZ',
                           help='Get frequency one octave higher')
    freq_group.add_argument('--octave-down', type=float, metavar='HZ',
                           help='Get frequency one octave lower')
    freq_parser.add_argument('--speed-of-sound', type=float, default=343.0,
                            help='Speed of sound (m/s, default: 343)')

    # Attenuation subcommand
    atten_parser = subparsers.add_parser('attenuation', help='Sound attenuation')
    atten_group = atten_parser.add_mutually_exclusive_group(required=True)
    atten_group.add_argument('--inverse-square', type=float, metavar='DISTANCE',
                            help='Calculate attenuation at distance (m)')
    atten_group.add_argument('--distance-for-level', type=float, metavar='LEVEL',
                            help='Find distance for target SPL level (dB)')
    atten_group.add_argument('--atmospheric', type=float, nargs=2,
                            metavar=('FREQUENCY', 'DISTANCE'),
                            help='Calculate atmospheric attenuation')
    atten_group.add_argument('--combined', type=float, nargs=2,
                            metavar=('DISTANCE', 'FREQUENCY'),
                            help='Combined geometric and atmospheric attenuation')
    atten_parser.add_argument('--reference-distance', type=float, default=1.0,
                             help='Reference distance (m, default: 1)')
    atten_parser.add_argument('--reference-level', type=float, default=100.0,
                             help='Reference SPL (dB, default: 100)')
    atten_parser.add_argument('--humidity', type=float, default=50.0,
                             help='Humidity (%, default: 50)')
    atten_parser.add_argument('--temperature', type=float, default=20.0,
                             help='Temperature (°C, default: 20)')

    return parser


def handle_db_command(args):
    """Handle decibel calculation commands."""
    try:
        if args.linear_to_db is not None:
            result = db.linear_to_db(args.linear_to_db, reference=args.reference)
            print(f"Linear {args.linear_to_db} = {result:.2f} dB (ref: {args.reference})")

        elif args.db_to_linear is not None:
            result = db.db_to_linear(args.db_to_linear, reference=args.reference)
            print(f"{args.db_to_linear} dB = {result:.6f} linear (ref: {args.reference})")

        elif args.spl is not None:
            result = db.sound_pressure_level(args.spl)
            print(f"Sound Pressure Level: {result:.2f} dB SPL")

        elif args.power_ratio is not None:
            result = db.power_ratio_to_db(args.power_ratio)
            print(f"Power ratio {args.power_ratio} = {result:.2f} dB")

        elif args.add_db is not None:
            result = db.db_add(args.add_db[0], args.add_db[1])
            print(f"{args.add_db[0]} dB + {args.add_db[1]} dB = {result:.2f} dB")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def handle_frequency_command(args):
    """Handle frequency calculation commands."""
    try:
        if args.hz_to_wavelength is not None:
            result = frequency.frequency_to_wavelength(args.hz_to_wavelength,
                                                      speed_of_sound=args.speed_of_sound)
            print(f"{args.hz_to_wavelength} Hz = {result:.3f} m wavelength")

        elif args.wavelength_to_hz is not None:
            result = frequency.wavelength_to_frequency(args.wavelength_to_hz,
                                                      speed_of_sound=args.speed_of_sound)
            print(f"{args.wavelength_to_hz} m = {result:.2f} Hz")

        elif args.note is not None:
            result = frequency.musical_note_frequency(args.note)
            print(f"Note {args.note} = {result:.2f} Hz")

        elif args.find_note is not None:
            note, freq, cents = frequency.frequency_to_musical_note(args.find_note)
            print(f"{args.find_note} Hz ≈ {note} ({freq:.2f} Hz, {cents:+.1f} cents)")

        elif args.octave_up is not None:
            result = frequency.octave_up(args.octave_up)
            print(f"{args.octave_up} Hz up one octave = {result:.2f} Hz")

        elif args.octave_down is not None:
            result = frequency.octave_down(args.octave_down)
            print(f"{args.octave_down} Hz down one octave = {result:.2f} Hz")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def handle_attenuation_command(args):
    """Handle attenuation calculation commands."""
    try:
        if args.inverse_square is not None:
            result = attenuation.inverse_square_law(
                args.inverse_square,
                reference_distance=args.reference_distance,
                reference_level=args.reference_level
            )
            print(f"SPL at {args.inverse_square}m = {result:.2f} dB")

        elif args.distance_for_level is not None:
            result = attenuation.distance_for_level(
                args.distance_for_level,
                reference_distance=args.reference_distance,
                reference_level=args.reference_level
            )
            print(f"Distance for {args.distance_for_level} dB = {result:.2f} m")

        elif args.atmospheric is not None:
            freq, dist = args.atmospheric
            result = attenuation.atmospheric_attenuation(
                freq, dist,
                humidity=args.humidity,
                temperature=args.temperature
            )
            print(f"Atmospheric attenuation: {freq} Hz, {dist} m = {result:.3f} dB")

        elif args.combined is not None:
            dist, freq = args.combined
            result = attenuation.combined_attenuation(
                dist, freq,
                reference_distance=args.reference_distance,
                reference_level=args.reference_level,
                humidity=args.humidity,
                temperature=args.temperature
            )
            print(f"Combined attenuation at {dist}m, {freq} Hz = {result:.2f} dB SPL")

    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    return 0


def main():
    """Main entry point for the CLI."""
    parser = setup_parser()
    args = parser.parse_args()

    # Show help if no command provided
    if not args.command:
        parser.print_help()
        return 0

    # Route to appropriate handler
    if args.command == 'db':
        return handle_db_command(args)
    elif args.command == 'frequency':
        return handle_frequency_command(args)
    elif args.command == 'attenuation':
        return handle_attenuation_command(args)

    return 0


if __name__ == '__main__':
    sys.exit(main())
