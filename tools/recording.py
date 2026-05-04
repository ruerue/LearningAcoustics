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

    # Save to wavfile/ in the project root (same level as src/ and tools/)
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wavfile_dir = os.path.join(project_root, 'wavfile')
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


def _configure_stereo_session(orientation='Front'):
    import objc_util
    objc_util.load_framework('AVFoundation')

    AVAudioSession = objc_util.ObjCClass('AVAudioSession')
    session = AVAudioSession.sharedInstance()

    session.setActive_error_(False, None)
    session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)

    available_inputs = session.availableInputs()
    builtin_port = None
    for i in range(len(available_inputs)):
        port = available_inputs[i]
        if str(port.portType()) == 'MicrophoneBuiltIn':
            builtin_port = port
            break

    if builtin_port is None:
        raise RuntimeError('内蔵マイクが見つかりません')

    session.setPreferredInput_error_(builtin_port, None)

    data_sources = builtin_port.dataSources()
    stereo_ds = None
    fallback_ds = None
    for i in range(len(data_sources)):
        ds = data_sources[i]
        patterns = ds.supportedPolarPatterns()
        if not patterns:
            continue
        has_stereo = any('Stereo' in str(patterns[j]) for j in range(len(patterns)))
        if has_stereo:
            if fallback_ds is None:
                fallback_ds = ds
            if orientation in str(ds.orientation()):
                stereo_ds = ds
                break

    if stereo_ds is None:
        stereo_ds = fallback_ds
    if stereo_ds is None:
        raise RuntimeError('ステレオ対応データソースが見つかりません')

    builtin_port.setPreferredDataSource_error_(stereo_ds, None)
    # 'Stereo' が正しい定数値（'AVAudioSessionPolarPatternStereo' は不可）
    stereo_ds.setPreferredPolarPattern_error_('Stereo', None)
    session.setActive_error_(True, None)
    session.setPreferredInputNumberOfChannels_error_(2, None)

    print(f'📡 マイク: {stereo_ds.dataSourceName()} ({stereo_ds.orientation()}) / Stereo')
    print(f'🎚️  チャンネル数: {session.inputNumberOfChannels()}')


def record_stereo(output_path, duration=5, orientation='Front'):
    """
    Record stereo audio using AVAudioRecorder via objc_util.

    Args:
        output_path: Full path to output WAV file
        duration:    Recording duration in seconds
        orientation: Mic orientation to prefer ('Front' or 'Back')

    Returns:
        output_path on success
    """
    import objc_util

    _configure_stereo_session(orientation)

    objc_util.load_framework('AVFoundation')
    AVAudioRecorder = objc_util.ObjCClass('AVAudioRecorder')
    AVAudioSession = objc_util.ObjCClass('AVAudioSession')
    NSURL = objc_util.ObjCClass('NSURL')

    settings = objc_util.ns({
        'AVFormatIDKey': 1819304813,  # kAudioFormatLinearPCM
        'AVSampleRateKey': 48000.0,
        'AVNumberOfChannelsKey': 2,
        'AVLinearPCMBitDepthKey': 16,
        'AVLinearPCMIsFloatKey': False,
        'AVLinearPCMIsBigEndianKey': False,
        'AVLinearPCMIsNonInterleaved': False,
    })

    url = NSURL.fileURLWithPath_(output_path)
    recorder = AVAudioRecorder.alloc().initWithURL_settings_error_(url, settings, None)

    if not recorder:
        raise RuntimeError('AVAudioRecorder の初期化に失敗しました')

    recorder.prepareToRecord()
    recorder.record()
    time.sleep(duration)
    recorder.stop()

    AVAudioSession.sharedInstance().setActive_error_(False, None)
    return output_path


def record_stereo_with_label(duration=5, orientation='Front'):
    """
    Record stereo audio with a user-supplied label via popup dialog.
    Saves to <project_root>/wavfile/YYYYMMDD_HHMMSS_<label>.wav

    Args:
        duration:    Recording duration in seconds
        orientation: Mic orientation to prefer ('Front' or 'Back')

    Returns:
        Path to the recorded file
    """
    import dialogs

    label = dialogs.input_alert(
        'ラベル入力',
        '録音ファイルのラベルを入力してください',
        '',
        'ラベル (例: test, stereo)'
    )
    if label is None:
        print('キャンセルされました')
        return None

    label = label.strip().replace(' ', '_')
    if not label:
        label = 'noname'

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f'{timestamp}_{label}.wav'

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wavfile_dir = os.path.join(project_root, 'wavfile')
    os.makedirs(wavfile_dir, exist_ok=True)

    output_path = os.path.join(wavfile_dir, filename)

    print(f'🎙️ ステレオ録音開始: {filename}')
    print(f'📍 時間: {duration} 秒')

    record_stereo(output_path, duration=duration, orientation=orientation)

    print(f'✓ 保存先: {output_path}')
    return output_path
