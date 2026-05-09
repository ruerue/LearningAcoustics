"""
Recording utilities for Pythonista
Provides audio recording functionality using Pythonista's Recorder class
"""

import json
import sound
import os
import time
from datetime import datetime


def _write_meta_sidecar(wav_path, **meta):
    """録音時のセッション情報を <basename>.meta.json として書き出す。

    convert_wav_to_npz が後で読んで、ユーザが明示的に渡さなかった
    audio_session_mode / mic_orientation / polar_pattern などを自動補完する。
    """
    base, _ = os.path.splitext(wav_path)
    meta_path = base + '.meta.json'
    with open(meta_path, 'w', encoding='utf-8') as f:
        json.dump(meta, f, ensure_ascii=False, indent=2, sort_keys=True)
    return meta_path


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
    # 直前に record_mono_calibrated を呼んでいた場合、AVAudioSession のモードが
    # 'Measurement' に残っていると Stereo polar pattern が利用不能なので、
    # 明示的に Default に戻す。
    session.setMode_error_('AVAudioSessionModeDefault', None)

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

    _write_meta_sidecar(
        output_path,
        device='iPhone built-in mic',
        mic_orientation=orientation,
        polar_pattern='Stereo',
        audio_session_mode='Default',
        recording_api='record_stereo',
        samplerate=48000,
        channels=2,
    )
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


def _configure_measurement_session(orientation=''):
    """Mono Measurement-mode session — AGC を無効化。

    iPhone 内蔵マイクでは Measurement モードと Stereo polar pattern が
    両立しないため、SPL 校正録音は mono に限定する。
    """
    import objc_util
    objc_util.load_framework('AVFoundation')

    AVAudioSession = objc_util.ObjCClass('AVAudioSession')
    session = AVAudioSession.sharedInstance()

    session.setActive_error_(False, None)
    session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)
    session.setMode_error_('AVAudioSessionModeMeasurement', None)

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

    if orientation:
        sources = builtin_port.dataSources()
        if sources is not None:
            for i in range(len(sources)):
                ds = sources[i]
                if orientation in str(ds.orientation()):
                    builtin_port.setPreferredDataSource_error_(ds, None)
                    break

    session.setActive_error_(True, None)
    session.setPreferredInputNumberOfChannels_error_(1, None)

    pin = session.preferredInput()
    actual_ds = pin.selectedDataSource() if pin is not None else None
    ds_name = str(actual_ds.dataSourceName()) if actual_ds is not None else ''
    ds_orient = str(actual_ds.orientation()) if actual_ds is not None else ''

    print(f'📡 マイク (Measurement): {ds_name} ({ds_orient}) / mono')
    print(f'🎚️  チャンネル数: {session.inputNumberOfChannels()}')

    return ds_name, ds_orient


def record_mono_calibrated(output_path, duration=5, orientation='', samplerate=48000):
    """SPL 校正前提の mono 録音 (AGC 無効化済み Measurement モード)。

    Args:
        output_path: 出力 WAV のフルパス
        duration:    録音秒数
        orientation: '' (システム既定。通常は Bottom Omnidirectional) もしくは
                     'Front' / 'Back' / 'Bottom' で内蔵マイクのデータソースを指定
        samplerate:  Hz (例 48000)

    Returns:
        output_path
    """
    import objc_util

    _, ds_orient = _configure_measurement_session(orientation)

    objc_util.load_framework('AVFoundation')
    AVAudioRecorder = objc_util.ObjCClass('AVAudioRecorder')
    AVAudioSession = objc_util.ObjCClass('AVAudioSession')
    NSURL = objc_util.ObjCClass('NSURL')

    settings = objc_util.ns({
        'AVFormatIDKey': 1819304813,  # kAudioFormatLinearPCM
        'AVSampleRateKey': float(samplerate),
        'AVNumberOfChannelsKey': 1,
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

    actual_orientation = (ds_orient or '').strip() or orientation or 'Front'
    _write_meta_sidecar(
        output_path,
        device='iPhone built-in mic',
        mic_orientation=actual_orientation,
        polar_pattern='Cardioid',
        audio_session_mode='Measurement',
        recording_api='record_mono_calibrated',
        samplerate=int(samplerate),
        channels=1,
    )
    return output_path


def _ask_label(title, prompt, hint):
    import dialogs
    label = dialogs.input_alert(title, prompt, '', hint)
    if label is None:
        return None
    label = label.strip().replace(' ', '_')
    return label or 'noname'


def _project_subdir(name):
    proj = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    d = os.path.join(proj, name)
    os.makedirs(d, exist_ok=True)
    return d


def record_calibrated(
    duration=5,
    label=None,
    output_path=None,
    orientation='',
    samplerate=48000,
):
    """SPL 校正用の mono 録音 (Measurement モード, AGC OFF)。

    すべて省略可:
        record_calibrated()                 # ラベルダイアログ → wavfile/ に保存
        record_calibrated(duration=10)      # 録音時間だけ指定
        record_calibrated(label='test')     # ダイアログ無しでラベル指定
        record_calibrated(output_path='/path/to/foo.wav')   # 直接指定

    Args:
        duration:    録音秒数
        label:       None でラベル入力ダイアログ。明示指定なら dialog なし。
                     output_path を渡せば label は無視される。
        output_path: フルパス指定。None ならラベル + タイムスタンプから生成。
        orientation: '' / 'Front' / 'Back' / 'Bottom' (内蔵マイクのデータソース)
        samplerate:  Hz (例 48000)

    Returns:
        保存パス。キャンセル時は None。
    """
    if output_path is None:
        if label is None:
            label = _ask_label(
                'ラベル入力',
                'SPL 校正用 mono 録音のラベル',
                'ラベル (例: test, room_noise)',
            )
            if label is None:
                print('キャンセルされました')
                return None
        else:
            label = (label or '').strip().replace(' ', '_') or 'noname'
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        wavfile_dir = _project_subdir('wavfile')
        output_path = os.path.join(wavfile_dir, f'{timestamp}_{label}.wav')

    print(f'🎙️ Mono 校正録音開始: {os.path.basename(output_path)}')
    print(f'📍 時間: {duration} 秒')

    record_mono_calibrated(
        output_path, duration=duration,
        orientation=orientation, samplerate=samplerate,
    )

    print(f'✓ 保存先: {output_path}')
    return output_path


def record_reference(
    duration=10,
    label=None,
    reference_db_spl=None,
    orientation='',
    samplerate=48000,
    save_as_default=True,
):
    """SPL 校正のための参照録音 + 校正実行をワンショットで行う。

    流れ:
        1. (label/reference_db_spl が None なら) ダイアログで入力
        2. Measurement モードで mono 録音 → ref_data/<date>_<label>.wav
        3. <wav>.meta.json サイドカー書き出し
        4. ref_data/<date>_<label>.npz に変換 (cal 値含む)
        5. save_as_default=True なら calibration_store.json にも保存

    以後の通常録音は record_calibrated() + convert_wav_to_npz() のみで
    自動的に dB SPL が出るようになる。

    Args:
        duration:         録音秒数 (default 10)
        label:            None でダイアログ
        reference_db_spl: SLM 等の読み値 (dB SPL)。None でダイアログ
        orientation:      '' / 'Front' / 'Back' / 'Bottom'
        samplerate:       Hz
        save_as_default:  True なら校正値を calibration_store に保存

    Returns:
        (npz_path, cal_db_spl_at_full_scale)。キャンセル時は (None, None)。
    """
    import dialogs

    if label is None:
        label = _ask_label(
            '校正参照録音',
            'ラベル (例: calref_pinknoise)',
            'ラベル',
        )
        if label is None:
            print('キャンセルされました')
            return None, None
    else:
        label = (label or '').strip().replace(' ', '_') or 'calref'

    if reference_db_spl is None:
        s = dialogs.input_alert(
            'SLM 読み値',
            'NIOSH SLM 等の読み値 (dB SPL, Leq 推奨)',
            '70.0',
            'dB SPL',
        )
        if s is None:
            print('キャンセルされました')
            return None, None
        try:
            reference_db_spl = float(s.strip())
        except (TypeError, ValueError):
            print(f'数値変換失敗: {s!r}')
            return None, None

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    refdir = _project_subdir('ref_data')
    wav_path = os.path.join(refdir, f'{timestamp}_{label}.wav')
    npz_path = wav_path.replace('.wav', '.npz')

    print(f'🎙️ 参照録音 (SLM={reference_db_spl} dB SPL): {os.path.basename(wav_path)}')
    print(f'📍 時間: {duration} 秒')
    record_mono_calibrated(
        wav_path, duration=duration,
        orientation=orientation, samplerate=samplerate,
    )
    print(f'✓ 保存先: {wav_path}')

    from .wav_dataset import convert_wav_to_npz, calibrate_from_reference
    convert_wav_to_npz(wav_path, npz_path)
    cal = calibrate_from_reference(
        npz_path, reference_db_spl,
        save_as_default=save_as_default,
        cal_method=f'NIOSH SLM transfer ({reference_db_spl:.2f} dB SPL)',
    )
    print(f'✓ cal_db_spl_at_full_scale = {cal:.2f}')
    if save_as_default:
        print('✓ calibration_store.json に保存しました')
    return npz_path, cal
