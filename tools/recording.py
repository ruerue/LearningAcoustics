"""
Recording utilities for Pythonista
Provides audio recording functionality using Pythonista's Recorder class
"""

import sound
import os
import time
from datetime import datetime


def record_with_label(duration=5):
    """
    Record audio with a user-supplied label via popup dialog.
    Saves to ~/Documents/wavfile/YYYYMMDD_HHMMSS_<label>.wav

    Args:
        duration: Recording duration in seconds

    Returns:
        Path to the recorded file
    """
    import dialogs

    label = dialogs.input_alert(
        'ラベル入力',
        '録音ファイルのラベルを入力してください',
        '',
        'ラベル (例: test, cat, dog)'
    )
    if label is None:
        print('キャンセルされました')
        return None

    label = label.strip().replace(' ', '_')
    if not label:
        label = 'noname'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{label}.wav'

    docs_dir = os.path.expanduser('~/Documents')
    wavfile_dir = os.path.join(docs_dir, 'wavfile')
    os.makedirs(wavfile_dir, exist_ok=True)

    output_path = os.path.join(wavfile_dir, filename)

    print(f'🎙️ 録音開始: {filename}')
    print(f'📍 時間: {duration} 秒')

    recorder = sound.Recorder(output_path)
    recorder.record()
    time.sleep(duration)
    recorder.stop()

    print(f'✓ 保存先: {output_path}')
    return output_path


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
