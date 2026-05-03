#!/usr/bin/env python3
"""
ラベル付き録音スクリプト
実行: python3 src/20260503_001_record_with_label.py

ポップアップでラベルを入力し、~/Documents/wavfile/YYYYMMDD_HHMMSS_<label>.wav に保存する。
"""

import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tools import record_with_label


def main():
    print('=' * 50)
    print('ラベル付き録音')
    print('=' * 50)

    duration = 5

    print(f'\n📝 録音時間: {duration} 秒')
    print('ポップアップにラベルを入力してください...\n')

    result = record_with_label(duration=duration)

    if result:
        print(f'\n✓ 録音完了: {result}')
    else:
        print('\n録音がキャンセルされました')
        sys.exit(0)


if __name__ == '__main__':
    main()
