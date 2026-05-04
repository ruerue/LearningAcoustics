#!/usr/bin/env python3
"""
ステレオ録音スクリプト
実行: python3 src/20260504_001_record_stereo.py

内蔵マイクのStereoポーラーパターンを使い、2chステレオWAVを録音する。
ポップアップでラベルを入力し、wavfile/YYYYMMDD_HHMMSS_<label>.wav に保存する。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import record_stereo_with_label


def main():
    print('=' * 50)
    print('ステレオ録音（内蔵マイク / 前面）')
    print('=' * 50)

    duration = 5
    orientation = 'Front'  # 'Front'（前面）または 'Back'（背面）

    print(f'\n📝 録音時間: {duration} 秒')
    print(f'📡 マイク向き: {orientation}')
    print('ポップアップにラベルを入力してください...\n')

    result = record_stereo_with_label(duration=duration, orientation=orientation)

    if result:
        print(f'\n✓ 録音完了: {result}')
    else:
        print('\n録音がキャンセルされました')
        sys.exit(0)


if __name__ == '__main__':
    main()
