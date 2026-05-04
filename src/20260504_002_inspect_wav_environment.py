#!/usr/bin/env python3
"""
Pythonista環境調査スクリプト

wavfile/ フォルダの WAV を読み込み、Pythonで扱いやすい形式で保存する
スクリプトを書く前段として、Pythonista 上で何が使えるかを調べる。

調査内容:
  1. 標準ライブラリの import 可否 (wave, struct, array, pickle, json, gzip, csv)
  2. サードパーティの import 可否 (numpy, scipy.io.wavfile, soundfile, h5py, matplotlib)
  3. wavfile/ フォルダの存在・WAV ファイル一覧
  4. 利用可能なライブラリでサンプル WAV のヘッダ/データを実際に読めるか
  5. 保存候補形式 (npy / npz / pickle / hdf5 / csv) の利用可否

実行:
    python3 src/20260504_002_inspect_wav_environment.py

書き込みは行わない。読み取りと import のみ。
"""

import sys
import os
import platform
import importlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def header(title):
    print()
    print('=' * 60)
    print(title)
    print('=' * 60)


def try_import(module_name, attr=None):
    """import を試みて結果を表示。成功時はモジュール、失敗時は None を返す。"""
    try:
        mod = importlib.import_module(module_name)
        if attr is not None:
            getattr(mod, attr)
        version = getattr(mod, '__version__', '(version 不明)')
        print(f'  [OK]  {module_name:<24}  {version}')
        return mod
    except Exception as e:
        print(f'  [NG]  {module_name:<24}  {type(e).__name__}: {e}')
        return None


def main():
    header('1. ランタイム情報')
    print(f'  Python    : {sys.version.split()[0]}')
    print(f'  実装      : {platform.python_implementation()}')
    print(f'  プラットフォーム: {platform.platform()}')
    print(f'  実行ファイル: {sys.executable}')
    print(f'  cwd       : {os.getcwd()}')

    header('2. 標準ライブラリ')
    std = {}
    for name in ['wave', 'struct', 'array', 'pickle', 'json',
                 'gzip', 'bz2', 'lzma', 'csv', 'sqlite3', 'base64']:
        std[name] = try_import(name)

    header('3. サードパーティ (数値計算 / 信号処理)')
    third = {}
    third['numpy']       = try_import('numpy')
    third['scipy']       = try_import('scipy')
    third['scipy.io']    = try_import('scipy.io.wavfile')
    third['scipy.signal']= try_import('scipy.signal')
    third['soundfile']   = try_import('soundfile')   # libsndfile ベース、iOS では基本不可
    third['h5py']        = try_import('h5py')
    third['pandas']      = try_import('pandas')
    third['matplotlib']  = try_import('matplotlib')

    header('4. Pythonista / iOS 固有モジュール (参考)')
    try_import('objc_util')
    try_import('sound')
    try_import('ui')
    try_import('dialogs')
    try_import('console')
    try_import('photos')

    header('5. wavfile/ フォルダ確認')
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    wavdir = os.path.join(project_root, 'wavfile')
    print(f'  対象パス: {wavdir}')
    if not os.path.isdir(wavdir):
        print('  [NG] wavfile/ が見つかりません')
        wav_files = []
    else:
        wav_files = sorted(
            f for f in os.listdir(wavdir)
            if f.lower().endswith('.wav')
        )
        print(f'  WAV ファイル数: {len(wav_files)}')
        for f in wav_files:
            full = os.path.join(wavdir, f)
            size = os.path.getsize(full)
            print(f'    - {f}  ({size:,} bytes)')

    header('6. サンプル WAV を実際に読んでみる')
    if not wav_files:
        print('  WAV ファイルが無いためスキップ')
    else:
        sample = os.path.join(wavdir, wav_files[0])
        print(f'  対象: {os.path.basename(sample)}')

        # 6-1. wave 標準モジュール
        print('\n  -- wave モジュール --')
        if std['wave']:
            try:
                import wave
                with wave.open(sample, 'rb') as w:
                    nch = w.getnchannels()
                    sw  = w.getsampwidth()
                    fr  = w.getframerate()
                    nf  = w.getnframes()
                    print(f'    チャンネル数 : {nch}')
                    print(f'    サンプル幅   : {sw} byte ({sw * 8} bit)')
                    print(f'    サンプリング : {fr} Hz')
                    print(f'    フレーム数   : {nf}')
                    print(f'    再生時間     : {nf / fr:.3f} s')
                    raw = w.readframes(min(nf, 8))
                    print(f'    先頭{min(nf, 8)}フレームの raw bytes 長: {len(raw)}')
            except Exception as e:
                print(f'    [NG] {type(e).__name__}: {e}')

        # 6-2. scipy.io.wavfile
        print('\n  -- scipy.io.wavfile --')
        if third['scipy.io']:
            try:
                from scipy.io import wavfile as sciwav
                fr, data = sciwav.read(sample)
                print(f'    サンプリング : {fr} Hz')
                print(f'    shape        : {data.shape}')
                print(f'    dtype        : {data.dtype}')
                print(f'    min/max      : {data.min()} / {data.max()}')
            except Exception as e:
                print(f'    [NG] {type(e).__name__}: {e}')
        else:
            print('    scipy 未導入のためスキップ')

        # 6-3. numpy で wave + frombuffer
        print('\n  -- wave + numpy.frombuffer --')
        if std['wave'] and third['numpy']:
            try:
                import wave
                import numpy as np
                with wave.open(sample, 'rb') as w:
                    nch = w.getnchannels()
                    sw  = w.getsampwidth()
                    nf  = w.getnframes()
                    raw = w.readframes(nf)
                dtype = {1: np.int8, 2: np.int16, 4: np.int32}.get(sw)
                if dtype is None:
                    print(f'    [NG] サンプル幅 {sw} byte は未対応')
                else:
                    arr = np.frombuffer(raw, dtype=dtype)
                    if nch > 1:
                        arr = arr.reshape(-1, nch)
                    print(f'    shape : {arr.shape}')
                    print(f'    dtype : {arr.dtype}')
                    print(f'    先頭5サンプル: {arr[:5].tolist()}')
            except Exception as e:
                print(f'    [NG] {type(e).__name__}: {e}')
        else:
            print('    wave か numpy が無いのでスキップ')

    header('7. 保存形式の利用可否（書き込みはしない）')
    candidates = [
        ('numpy .npy  (np.save)',         third['numpy']),
        ('numpy .npz  (np.savez/_compressed)', third['numpy']),
        ('pickle      (.pkl)',             std['pickle']),
        ('json        (メタ情報のみ)',      std['json']),
        ('gzip付きpickle (.pkl.gz)',       std['pickle'] and std['gzip']),
        ('HDF5        (h5py)',             third['h5py']),
        ('CSV         (大きく非推奨)',      std['csv']),
        ('sqlite3     (.db)',              std['sqlite3']),
    ]
    for label, ok in candidates:
        mark = '[OK]' if ok else '[NG]'
        print(f'  {mark}  {label}')

    header('8. まとめ / 次ステップ提案')
    if third['numpy']:
        print('  numpy が使えるので、推奨は np.savez_compressed で')
        print('  .npz に [サンプル配列, サンプリングレート, チャンネル数, 元ファイル名] を')
        print('  まとめて保存する形式。')
    else:
        print('  numpy が無い場合は pickle にタプル/辞書として保存するのが簡便。')
    print('  上記 [OK] の組み合わせを見て、実装スクリプトの方針を決める。')

    print('\n=== 調査完了 ===')


if __name__ == '__main__':
    main()
