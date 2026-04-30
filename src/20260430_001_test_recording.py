#!/usr/bin/env python3
"""
Test recording script
実行: python3 src/20260430_001_test_recording.py
"""

import sys
import os

# Add parent directory to path to import tools
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import record_audio_simple


def main():
    """Execute recording test"""
    print("=" * 50)
    print("Pythonista Recording Test")
    print("=" * 50)

    try:
        # Record 5 seconds of audio
        output_file = "test_recording.wav"
        duration = 5

        print(f"\n📝 Recording for {duration} seconds...")
        print("Please speak into the microphone...\n")

        result = record_audio_simple(output_file, duration=duration)

        print(f"\n✓ Successfully recorded: {result}")
        print("\nRecording completed!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
