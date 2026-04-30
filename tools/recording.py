"""
Recording utilities for Pythonista
Provides audio recording functionality using AVAudioRecorder
"""

import objc_util
import os
from datetime import datetime
from pathlib import Path

# Import iOS frameworks (Pythonista)
AVFoundation = objc_util.load_framework('AVFoundation')
Foundation = objc_util.load_framework('Foundation')


def record_audio(filename, duration=5, sample_rate=44100):
    """
    Record audio using Pythonista's audio capabilities

    Args:
        filename: Output file name (will be saved to Documents)
        duration: Recording duration in seconds
        sample_rate: Sample rate in Hz

    Returns:
        Path to the recorded file
    """
    try:
        # Get Documents directory
        docs_dir = os.path.expanduser('~/Documents')
        output_path = os.path.join(docs_dir, filename)
        os.makedirs(docs_dir, exist_ok=True)

        # Create NSURL for the output file
        file_url = Foundation.NSURL.fileURLWithPath_(output_path)

        # Create audio settings
        settings = {
            AVFoundation.AVFormatIDKey: 1633772320,  # kAudioFormatLinearPCM
            AVFoundation.AVSampleRateKey: sample_rate,
            AVFoundation.AVNumberOfChannelsKey: 1,
            AVFoundation.AVLinearPCMBitDepthKey: 16,
        }
        settings_dict = Foundation.NSDictionary.dictionaryWithDictionary_(settings)

        # Create audio session
        session = AVFoundation.AVAudioSession.sharedInstance()
        session.setCategory_mode_options_error_(
            AVFoundation.AVAudioSessionCategoryRecord,
            AVFoundation.AVAudioSessionModeDefault,
            0,
            None
        )
        session.setActive_withOptions_error_(True, 1, None)

        # Create recorder
        recorder = AVFoundation.AVAudioRecorder.alloc().initWithURL_settings_error_(
            file_url, settings_dict, None
        )

        if not recorder:
            raise Exception("Failed to initialize audio recorder")

        # Record
        recorder.record()
        print(f"🎙️ Recording started: {filename}")

        # Wait for specified duration
        import time
        time.sleep(duration)

        # Stop recording
        recorder.stop()
        session.setActive_withOptions_error_(False, 1, None)

        print(f"✓ Recording saved to: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Recording error: {e}")
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
    return record_audio(filename, duration=duration, sample_rate=44100)
