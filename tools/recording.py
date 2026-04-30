"""
Recording utilities for Pythonista
Provides audio recording functionality using AVAudioRecorder
"""

import objc_util
import os
import time


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

        # Load frameworks using objc_util
        AVFoundation = objc_util.load_framework('AVFoundation')
        Foundation = objc_util.load_framework('Foundation')

        # Create NSURL for the output file using alloc/init pattern
        file_url = objc_util.ObjCClass('NSURL').fileURLWithPath_(output_path)

        # Create audio settings dictionary
        settings = {
            'AVFormatIDKey': 1633772320,  # kAudioFormatLinearPCM
            'AVSampleRateKey': sample_rate,
            'AVNumberOfChannelsKey': 1,
            'AVLinearPCMBitDepthKey': 16,
        }

        # Create recorder with settings
        error = objc_util.c_void_p()
        NSMutableDictionary = objc_util.ObjCClass('NSMutableDictionary')
        settings_dict = NSMutableDictionary.dictionaryWithDictionary_(settings)

        AVAudioRecorder = objc_util.ObjCClass('AVAudioRecorder')
        recorder = AVAudioRecorder.alloc().initWithURL_settings_error_(
            file_url, settings_dict, error
        )

        if not recorder:
            raise Exception("Failed to initialize audio recorder")

        # Setup audio session
        AVAudioSession = objc_util.ObjCClass('AVAudioSession')
        session = AVAudioSession.sharedInstance()

        # Set category for recording
        session.setCategory_mode_options_error_(
            'AVAudioSessionCategoryRecord',
            'AVAudioSessionModeDefault',
            0,
            None
        )
        session.setActive_withOptions_error_(True, 1, None)

        # Record
        recorder.record()
        print(f"🎙️ Recording started: {filename}")
        print(f"📍 Duration: {duration} seconds")

        # Wait for specified duration
        time.sleep(duration)

        # Stop recording
        recorder.stop()
        session.setActive_withOptions_error_(False, 1, None)

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
    return record_audio(filename, duration=duration, sample_rate=44100)
