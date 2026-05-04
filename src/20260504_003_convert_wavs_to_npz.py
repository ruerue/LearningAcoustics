#!/usr/bin/env python3
"""
wavfile/*.wav を dataset/*.npz に一括変換する。

実行: python3 src/20260504_002_convert_wavs_to_npz.py

各 .npz には samples 本体 + サンプリングレート / チャンネル / dtype 情報 +
将来の dB SPL 校正用フィールド (cal_db_spl_at_full_scale 等) を含む。
スキーマの詳細は tools/wav_dataset.py の docstring を参照。

実行後、最初の 1 件をロードし直して shape / RMS / dBFS を確認する。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import convert_dir, load_npz


def main():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    src_dir = os.path.join(project_root, 'wavfile')
    out_dir = os.path.join(project_root, 'dataset')

    print('=' * 60)
    print('WAV -> NPZ 変換')
    print('=' * 60)
    print('SRC:', src_dir)
    print('OUT:', out_dir)
    print('-' * 60)

    out_paths = convert_dir(src_dir, out_dir, verbose=True)

    print('-' * 60)
    print('変換完了:', len(out_paths), '件')

    if not out_paths:
        return

    print()
    print('=== 試し読み (最初の 1 件) ===')
    rec = load_npz(out_paths[0])
    print(rec)
    print('  samples shape :', rec.samples.shape, 'dtype:', rec.samples.dtype)
    print('  duration_sec  :', rec.duration_sec)
    print('  full_scale    :', rec.full_scale)
    print('  RMS (linear)  :', rec.rms())
    print('  dBFS          :', rec.dbfs())
    print('  dB SPL        :', rec.db_spl(), '  (校正済み:', rec.is_calibrated, ')')


if __name__ == '__main__':
    main()
