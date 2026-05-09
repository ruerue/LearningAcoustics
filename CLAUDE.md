# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LearningAcoustics** is a Pythonista-based audio recording and processing project designed to run on iOS devices through the Pythonista app and Working Copy integration. The primary workflow involves developing audio capture and analysis tools that execute directly on iOS.

## Development Workflow

### Branch Strategy
- **Development branch**: `claude/iphone-multichannel-audio-FgrVc`
- All development and commits should go to this branch
- Push changes with: `git push -u origin claude/iphone-multichannel-audio-FgrVc`
- Tested via Working Copy on iOS before finalizing

### Architecture

The project follows a clear separation of concerns:

```
tools/               # Reusable modules and functions
├── recording.py     # Audio capture functionality (mono & stereo)
├── wav_dataset.py   # WAV <-> NPZ 変換 / ロード / 校正ヘルパー
└── __init__.py

src/                 # Execution scripts (iOS ready)
├── 20260430_001_test_recording.py
├── 20260503_001_record_with_label.py
├── 20260504_001_record_stereo.py
├── 20260504_002_inspect_wav_environment.py   # Pythonista 環境調査
├── 20260504_003_convert_wavs_to_npz.py       # wavfile/ -> dataset/ 変換
└── __init__.py

wavfile/             # Recorded WAV files (auto-created at runtime)
dataset/             # WAV から変換した .npz (解析用、auto-created)
```

### Key Principles

1. **tools/** folder contains:
   - Reusable functions and classes
   - Pythonista-compatible iOS API wrappers
   - Imported by src/ scripts and external code

2. **src/** folder contains:
   - Executable scripts that can be run directly in Pythonista
   - Naming convention: `YYYYMMDD_NNN_content_description.py`
   - Each file is self-contained and importable as a module
   - Incremental numbering (001, 002, etc.) for scripts on the same day

### Pythonista Integration

Scripts must be compatible with Pythonista's environment:
- Use `objc_util` (not `objc`) for iOS API access - `objc_util.load_framework('FrameworkName')`
- Assume `sys.path` includes the parent directory for importing tools/
- Path handling: Use `os.path.expanduser('~/Documents')` for file storage
- All imports should handle Pythonista's limited stdlib gracefully

Example execution:
```bash
# From Pythonista or terminal
python3 src/20260504_001_record_stereo.py
```

### Pythonista-Specific Fixes

**iOS API Access:**
- **Error**: `ModuleNotFoundError: No module named 'objc'`
- **Solution**: Use `objc_util` instead, which is Pythonista's native wrapper
  ```python
  import objc_util
  Framework = objc_util.load_framework('FrameworkName')
  ```

**ObjC Classes in Pythonista:**
- **Error**: `'bool' object has no attribute 'NSURL'` or similar
- **Solution**: Use `objc_util.ObjCClass()` to access Objective-C classes directly
  ```python
  import objc_util
  NSURL = objc_util.ObjCClass('NSURL')
  url = NSURL.fileURLWithPath_(filepath)
  ```
- Load frameworks at function level, not module level
- Use string keys for ObjC method names and dictionary access

**Path imports in src/ scripts:**
- Scripts in src/ need to import from tools/ folder
- Use: `sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))`
- This adds the parent directory to Python path

### Working Copy Workflow

1. Push changes to development branch
2. Pull in Working Copy on iOS
3. Open script in Pythonista from Working Copy
4. Run and verify functionality
5. If working, commit with clear messages

## Development Workflow with Claude Code

### Commits and Pushes
- **Only commit and push when explicitly instructed**
- Claude Code will change files and report modifications at the end of each response
- You verify changes work before requesting commit/push
- This speeds up iteration by avoiding unnecessary commits

### File Changes Reporting
- Claude Code will always display modified files at the end
- Use copy-paste from terminal to manually commit when ready
- Format: provide exact `git add` and `git commit` commands needed

## Common Commands

```bash
# Check status
git status

# Commit changes
git add <files>
git commit -m "Description of changes"

# Push to development branch
git push -u origin claude/iphone-multichannel-audio-FgrVc

# View recent commits
git log --oneline -5
```

## File Structure Guidelines

- **New tools**: Add to `tools/` with descriptive names, then import in `tools/__init__.py`
- **New scripts**: Create in `src/` with format `YYYYMMDD_NNN_description.py`
- **Dependencies**: Declare in `Pipfile` if adding external packages

## Testing on iOS

1. Code must work within Pythonista's sandbox
2. WAV files are saved to `wavfile/` in the project root (Working Copy File Provider Storage)
3. Test by running directly in Pythonista via Working Copy
4. Verify output files appear in `wavfile/` folder

## Pythonista Audio Recording

### Mono Recording — `sound.Recorder`

Pythonista's built-in `sound.Recorder` for simple mono recording:

```python
import sound
recorder = sound.Recorder(filepath)
recorder.record()
# ... wait for duration ...
recorder.stop()
```

### Stereo Recording — `AVAudioRecorder` via `objc_util`

For stereo (2ch) recording using the iPhone's built-in microphones:

```python
from tools import record_stereo_with_label
path = record_stereo_with_label(duration=5)              # 前面マイク（デフォルト）
path = record_stereo_with_label(duration=5, orientation='Back')  # 背面マイク
```

**Verified on device**: iPhone内蔵マイクのStereoポーラーパターンで2chステレオ録音動作確認済み（2026-05-04）。

### SPL 校正用 Mono 録音 — `record_mono_calibrated_with_label`

`AVAudioSessionModeMeasurement` で AGC を無効化した mono 録音。SPL 校正値が物理的意味を持つのはこの API で撮ったファイルのみ。

```python
from tools import record_mono_calibrated_with_label
path = record_mono_calibrated_with_label(duration=5)                   # システム既定 (通常 Bottom Omnidirectional)
path = record_mono_calibrated_with_label(duration=5, orientation='Front')  # 内蔵マイクの前面データソース
```

**実機検証結果（2026-05-09, iOS 26.4.2 / iPhone12,8）**: Measurement モードと Stereo polar pattern は **両立不可**。Measurement に切り替えると `port.dataSources()` の supportedPolarPatterns から Stereo が外れ、`setPreferredInputNumberOfChannels(2)` も `False` で蹴られる。`session.inputGain settable=False` なので手動ゲイン固定もできず、Measurement モードが AGC を切る唯一の手段。

→ 用途別に API を二段構え:
- 楽しみ用ステレオ録音 → `record_stereo_with_label` (Default mode + Stereo polar)
- SPL 校正録音 / 解析用 → `record_mono_calibrated_with_label` (Measurement mode + mono)

#### AVAudioSession ステレオ設定の正しい順序

```python
session.setActive_error_(False, None)
session.setCategory_error_('AVAudioSessionCategoryPlayAndRecord', None)
session.setPreferredInput_error_(builtin_mic_port, None)
port.setPreferredDataSource_error_(stereo_data_source, None)
data_source.setPreferredPolarPattern_error_('Stereo', None)  # ← 'Stereo' が正しい（'AVAudioSessionPolarPatternStereo' は不可）
session.setActive_error_(True, None)
session.setPreferredInputNumberOfChannels_error_(2, None)
```

#### AVAudioRecorder ステレオ設定

```python
settings = objc_util.ns({
    'AVFormatIDKey': 1819304813,  # kAudioFormatLinearPCM
    'AVSampleRateKey': 48000.0,
    'AVNumberOfChannelsKey': 2,
    'AVLinearPCMBitDepthKey': 16,
    'AVLinearPCMIsFloatKey': False,
    'AVLinearPCMIsBigEndianKey': False,
    'AVLinearPCMIsNonInterleaved': False,
})
```

#### iPhone 内蔵マイクのステレオ対応状況

| データソース | 場所 | ステレオ対応 |
|---|---|---|
| 下 (Bottom) | Lower | 非対応（Omnidirectionalのみ） |
| 前面 (Front) | Upper/Front | **対応** |
| 背面 (Back) | Upper/Back | **対応** |

## WAV File Saving Convention

### Save Location

All WAV recordings are saved to:
```
<project_root>/wavfile/
```

This is the `wavfile/` folder at the same level as `src/` and `tools/`. It is created automatically at runtime if it does not exist.

On iOS via Working Copy, the actual path resolves to:
```
/private/var/mobile/Containers/Shared/AppGroup/.../File Provider Storage/Repositories/LearningAcoustics/wavfile/
```

### File Naming Format

```
YYYYMMDD_HHMMSS_<label>.wav
```

- `YYYYMMDD` — Recording date (e.g. `20260504`)
- `HHMMSS`   — Recording start time (e.g. `105248`)
- `<label>`  — User-supplied label entered in a popup dialog each time

Example: `20260504_105248_test.wav`

### Label Input (Popup Dialog)

Both `record_with_label()` (mono) and `record_stereo_with_label()` (stereo) trigger a Pythonista popup (`dialogs.input_alert`) that asks for a label before each recording. Spaces are replaced with underscores; empty input defaults to `noname`.

```python
from tools import record_with_label, record_stereo_with_label

# モノラル
path = record_with_label(duration=5)

# ステレオ
path = record_stereo_with_label(duration=5)
```

## Multi-channel Recording (4ch+)

4チャンネル以上の録音には外部ハードウェアが必要。

| チャンネル数 | 必要なハードウェア | 接続 |
|---|---|---|
| 2ch（ステレオ） | 不要（内蔵マイク） | — |
| 4ch | IK Multimedia iRig Pro Quattro I/O / MOTU M4 / Focusrite Scarlett 4i4 | USB-C (iPhone 15+) or Lightning adapter |
| 8ch | Zoom UAC-8 / MOTU M6 | USB-C or Lightning adapter |

**条件**: iOS対応にはUSB Audio Class-Compliant（クラスコンプライアント）であることが必須。

## Pythonista 環境調査結果 (2026-05-04 実機確認)

`src/20260504_002_inspect_wav_environment.py` を iPhone (iOS 26.4.2 / iPhone12,8) 上で実行した結果。

### ランタイム
- Python 3.10.4 (CPython)
- cwd は Working Copy の File Provider Storage 内 (LearningAcoustics 直下)

### 標準ライブラリ
| モジュール | 可否 | メモ |
|---|---|---|
| `wave`, `struct`, `array` | OK | WAV 読み書きの基盤 |
| `pickle`, `json`, `csv`, `sqlite3`, `base64` | OK | |
| `gzip`, `bz2` | OK | 圧縮利用可 |
| `lzma` | **NG** | `_lzma` モジュールが無い (Pythonista のビルド都合) |

### サードパーティ
| ライブラリ | 可否 | バージョン |
|---|---|---|
| `numpy` | OK | 1.22.3 |
| `pandas` | OK | 1.4.4 |
| `matplotlib` | OK | 3.3.3+0.g5a4f1b675d.dirty |
| `scipy` (含 `scipy.io.wavfile` / `scipy.signal`) | **NG** | 未導入 |
| `soundfile` | **NG** | libsndfile が無く iOS では事実上不可 |
| `h5py` | **NG** | 未導入 |

### 結論: 解析データの永続化形式
- **採用**: `np.savez_compressed` による `.npz` 保存
  - 理由: numpy のみで完結 / 圧縮が効く (実測 60–82%) / 文字列・スカラー・配列を辞書状にまとめられる / scipy/h5py 不要
- 補助: 必要なら `pickle.gz` も使えるが ndarray 中心なら `.npz` が直行
- 非採用: scipy.io.wavfile / soundfile / h5py (未導入のため)

### WAV 読み込みの定石 (Pythonista 上)
```python
import wave, numpy as np
w = wave.open(path, 'rb')
nch, sw, fr, nf = w.getnchannels(), w.getsampwidth(), w.getframerate(), w.getnframes()
raw = w.readframes(nf); w.close()
arr = np.frombuffer(raw, dtype=np.int16)
if nch > 1:
    arr = arr.reshape(-1, nch)
```

### Pythonista でのコピペ実行に関する注意点
- **シェバング (`#!/...`) は1行目で SyntaxError** になることがある → ベタ打ち版では除く
- **「Globals == Locals」モード**では関数本体内の空行が解釈区切りになりうる → 関数内に空行を置かない
- ドット付きモジュール名 (例: `from scipy.io import ...`) はレンダラー経由で自動リンク化されて `<scipy.io>` に化けるケースが確認されたため、コピペ用コードでは `importlib.import_module('scipy.io.wavfile')` を使う

## NPZ Dataset Schema (v1.1)

`tools/wav_dataset.py` の `convert_wav_to_npz()` が出力する `.npz` のキー一覧。
将来の周波数表示・dB SPL 表示・校正運用を見越して拡張余地を持たせている。

| キー | 型 | 役割 |
|---|---|---|
| `samples` | ndarray int16 (N,) or (N, ch) | 生サンプル本体 |
| `sample_dtype` | str | `'int16'` 等 |
| `samplerate` | int32 | Hz |
| `channels` | int32 | チャンネル数 |
| `bit_depth` | int32 | 16 等 |
| `n_frames` | int64 | サンプル数 |
| `duration_sec` | float64 | 再生時間 |
| `full_scale` | float64 | int → float 正規化の分母 (int16 なら 32768.0) |
| `source` | str | 元 WAV ファイル名 |
| `recorded_at` | str | `'YYYYMMDD_HHMMSS'` (ファイル名から自動抽出) |
| `label` | str | ファイル名末尾のラベル |
| `device` | str | `'iPhone built-in mic'` 等 |
| `mic_orientation` | str | `'Front'` / `'Back'` / `'Bottom'` / `''` |
| `polar_pattern` | str | `'Stereo'` / `'Cardioid'` / `'Omnidirectional'` / `''` |
| `audio_session_mode` *(v1.1+)* | str | `'Measurement'` (AGC off, SPL校正可) / `'Default'` (AGC on, SPL校正不可) / `''` |
| `preamp_gain_db` | float64 | 外部ゲイン (dB) |
| `cal_db_spl_at_full_scale` | float64 | フルスケール = 何 dB SPL か (NaN=未校正) |
| `cal_ref_freq_hz` | float64 | 校正基準周波数 (NaN=未校正) |
| `cal_method` | str | 校正方法のメモ |
| `cal_date` | str | 校正実施日 |
| `preprocess` | str | 前処理メモ |
| `notes` | str | 自由記述 |
| `schema_version` | str | `'1.1'` |

### v1.0 → v1.1 互換性

- 追加キーのみ (`audio_session_mode`)。既存キーの型・意味は不変。
- v1.0 で書かれた `.npz` を `load_npz()` で読むと `audio_session_mode=''` (不明) として扱う。
- 既存 `.npz` に後追い記入したい場合は `update_calibration(path, audio_session_mode='Measurement' or 'Default')` で OK。

### SPL 校正の信頼性ルール

`WavRecord.is_calibration_trustworthy` は **「校正済 AND `audio_session_mode == 'Measurement'`」** のときのみ `True`。

- iPhone 内蔵マイクは `inputGain settable=False`（実機検証済 2026-05-09）なので、AGC を切る唯一の手段が Measurement モード。
- Default モード録音に校正値を入れても、入力レベルが変わると AGC ゲインが動いて絶対 SPL は信用できない。
- `db_spl()` はこの条件を満たさないとき warning を出すが値は返す（相対比較目的の用途のため）。

### dB SPL の換算式 (校正済みの場合)
```
SPL_dB = 20 * log10(rms_float) + cal_db_spl_at_full_scale - preamp_gain_db
```
- `rms_float` は `samples / full_scale` の RMS (-1〜1 正規化)
- 校正は `tools.update_calibration(npz_path, cal_db_spl_at_full_scale=..., ...)` で後追い記入できる

### 使い方
```python
from tools import convert_dir, load_npz, update_calibration

# 一括変換
convert_dir('wavfile', 'dataset')

# 読み込み
rec = load_npz('dataset/20260504_105248_test.npz')
rec.samples            # ndarray (N, ch) int16
rec.to_float()         # ndarray (N, ch) float32, -1.0~1.0
rec.channel(0)         # 左ch のみ
rec.time_axis()        # 秒軸 (N,)
rec.rms(); rec.dbfs()  # RMS / dBFS
rec.db_spl()           # 校正済みなら dB SPL、未校正なら NaN

# 後から校正情報を埋める
update_calibration(
    'dataset/20260504_105248_test.npz',
    cal_db_spl_at_full_scale=120.0,  # 例: 1Pa = 94dB SPL を基準に算出した値
    cal_ref_freq_hz=1000.0,
    cal_method='B&K 4231 ピストンホン (94 dB SPL @ 1 kHz)',
)
```

## 今後の予定 (Roadmap)

### B案 (`tools/wav_dataset.py` の機能拡張)
保存スキーマは v1.0 で固まったので、以下は読み込み側に追加していく方針:

1. **周波数解析ヘルパー** (numpy のみで実装。scipy 不可のため `np.fft` を使用)
   - `WavRecord.spectrum(channel=0, n_fft=None, window='hann')` → (freq, magnitude_db)
   - `WavRecord.spectrogram(channel=0, n_fft=2048, hop=512, window='hann')` → (freqs, times, S_db)
   - 窓関数は `np.hanning` / `np.hamming` / `np.blackman` などを内製ディスパッチ
2. **dB SPL 表示**
   - `WavRecord.db_spl_series(channel=0, frame_ms=125)` → 時間連続 SPL
   - 校正済みのみ動作、未校正なら明示的に `RuntimeError`
3. **可視化 (matplotlib)**
   - 別モジュール `tools/plotting.py` を作る案
   - 波形 / スペクトル / スペクトログラム / dB SPL タイムライン
4. **校正ワークフロー**
   - ピストンホン (94 dB SPL @ 1 kHz 等) 録音から `cal_db_spl_at_full_scale` を自動算出するヘルパー
   - `tools.calibrate_from_reference(npz_path, ref_db_spl=94.0, ref_freq_hz=1000.0)`

### スキーマを増やす際のルール
- 既存キーの**型・意味は変更しない**
- 追加キーのみ許可、未設定時は NaN / 空文字
- `schema_version` を上げる際は `tools/wav_dataset.py` の docstring を更新

## Notes for Future Work

- Pythonista has limited stdlib; test any new packages compatibility
- iOS file permissions require specific handling for ~/Documents access
- Stereo recording uses `AVAudioRecorder` via `objc_util`; mono uses `sound.Recorder`
- Multi-channel (4ch+) requires external USB audio interface + `AVAudioEngine` implementation
- Scripts should print progress/status for user feedback in Pythonista console
- 解析用データは `dataset/*.npz` (numpy) で保持。scipy/soundfile/h5py は実機に無いので使わない
