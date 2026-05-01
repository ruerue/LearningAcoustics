"""
Recording utilities for Pythonista
Provides audio recording functionality using Pythonista's Recorder class
"""

import sound
import os
import time


def record_audio(filename, duration=5):
    """
    Record audio using Pythonista's sound.Recorder class

    Args:
        filename: Output file name (will be saved to Documents)
        duration: Recording duration in seconds

    Returns:
        Path to the recorded file
    """
    try:
        # Get Documents directory
        docs_dir = os.path.expanduser('~/Documents')
        output_path = os.path.join(docs_dir, filename)
        os.makedirs(docs_dir, exist_ok=True)

        print(f"🎙️ Recording started: {filename}")
        print(f"📍 Duration: {duration} seconds")

        # Create and start recorder (path is required argument)
        recorder = sound.Recorder(output_path)
        recorder.record()

        # Wait for specified duration
        time.sleep(duration)

        # Stop recording (auto-saves to the specified path)
        recorder.stop()

        print(f"✓ Recording saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Recording error: {e}")
        import traceback
        traceback.print_exc()
        raise


def record_audio_simple(filename, duration=5):
    """
    Simplified audio recording for basic use

    Args:
        filename: Output file name
        duration: Recording duration in seconds

    Returns:
        Path to the recorded file
    """
    return record_audio(filename, duration=duration)
