"""
Recording utilities for Pythonista
Provides audio recording functionality using Pythonista's Recorder class
"""

import sound
import os


def record_audio(filename, duration=5, channels=1):
    """
    Record audio using Pythonista's sound.Recorder class

    Args:
        filename: Output file name (will be saved to Documents)
        duration: Recording duration in seconds
        channels: Number of audio channels (1=mono, 2=stereo)

    Returns:
        Path to the recorded file
    """
    try:
        # Get Documents directory
        docs_dir = os.path.expanduser('~/Documents')
        output_path = os.path.join(docs_dir, filename)
        os.makedirs(docs_dir, exist_ok=True)

        print(f"🎙️ Recording started: {filename}")
        print(f"📍 Duration: {duration} seconds, Channels: {channels}")

        # Create and start recorder
        recorder = sound.Recorder(channels=channels)
        recorder.start()

        # Wait for specified duration
        import time
        time.sleep(duration)

        # Stop recording and get audio data
        recorder.stop()
        audio = recorder.audio

        # Save to file
        audio.export(output_path, 'wav')

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
    return record_audio(filename, duration=duration, channels=1)
