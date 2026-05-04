# LearningAcoustics

iPhoneでPythonistaを使って音声を録音・分析するプロジェクト。Working Copy経由でiOS上で直接動作する。

## 動作環境

- **iOS**: iPhone（内蔵マイクでステレオ録音確認済み）
- **Pythonista 3**: スクリプト実行環境
- **Working Copy**: Gitクライアント（iOS上でリポジトリを管理）

## できること

| 機能 | スクリプト | チャンネル |
|---|---|---|
| モノラル録音（ラベル付き） | `src/20260503_001_record_with_label.py` | 1ch |
| **ステレオ録音（ラベル付き）** | `src/20260504_001_record_stereo.py` | **2ch** |

## クイックスタート

### Pythonistaで実行

1. Working Copy でリポジトリをクローン
2. Pythonista でスクリプトを開いて実行

```python
# ステレオ録音
from tools import record_stereo_with_label
path = record_stereo_with_label(duration=5)
```

```python
# モノラル録音
from tools import record_with_label
path = record_with_label(duration=5)
```

### 保存先

録音ファイルは `wavfile/` フォルダに自動保存される。

```
YYYYMMDD_HHMMSS_<label>.wav
例: 20260504_105248_test.wav
```

## プロジェクト構成

```
LearningAcoustics/
├── tools/
│   ├── __init__.py
│   └── recording.py          # 録音ユーティリティ（mono/stereo）
├── src/
│   ├── 20260430_001_test_recording.py
│   ├── 20260503_001_record_with_label.py
│   └── 20260504_001_record_stereo.py
├── wavfile/                  # 録音済みWAVファイル（自動作成）
├── CLAUDE.md
└── README.md
```

## ステレオ録音の仕組み

iPhoneの内蔵マイク（前面または背面）の **Stereoポーラーパターン** を使って2chステレオWAVを録音する。`sound.Recorder`（Pythonista組み込み）ではなく、`objc_util` 経由で `AVAudioRecorder` を直接操作することでステレオに対応。

```
内蔵マイク（前面）
├── Omnidirectional
├── Cardioid
└── Stereo  ← これを使用

内蔵マイク（背面）
├── Omnidirectional
├── Subcardioid
└── Stereo  ← これを使用
```

### 重要な知見

- ポーラーパターンの設定文字列は `'Stereo'`（`'AVAudioSessionPolarPatternStereo'` は動作しない）
- AVAudioSession の設定順序が重要（セッション → ポート → データソース → パターン → 再アクティブ化）
- サンプルレートはデバイスのネイティブ値 48000 Hz を使用

## 多チャンネル録音（4ch以上）について

4チャンネル以上の録音には外部USBオーディオインターフェースが必要。

| チャンネル | ハードウェア例 | 接続 |
|---|---|---|
| 4ch | IK Multimedia iRig Pro Quattro I/O | Lightning / USB-C |
| 4ch | MOTU M4 / Focusrite Scarlett 4i4 | USB-C（iPhone 15+） |
| 8ch | Zoom UAC-8 | USB-C or Lightning adapter |

iOSで使用するには **USB Audio Class-Compliant** 対応製品であることが必要。

## API リファレンス

### `tools.record_stereo_with_label(duration=5, orientation='Front')`

ポップアップでラベルを入力してステレオ録音する。

- `duration`: 録音時間（秒）
- `orientation`: マイク向き（`'Front'` または `'Back'`）
- 戻り値: 保存先パス文字列（キャンセル時は `None`）

### `tools.record_stereo(output_path, duration=5, orientation='Front')`

指定パスにステレオWAVを録音する（ラベルダイアログなし）。

### `tools.record_with_label(duration=5)`

ポップアップでラベルを入力してモノラル録音する（`sound.Recorder` 使用）。

### `tools.record_audio(filename, duration=5)`

指定ファイル名でモノラル録音する（`~/Documents/` に保存）。
