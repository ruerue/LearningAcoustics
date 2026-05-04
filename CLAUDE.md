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
└── __init__.py

src/                 # Execution scripts (iOS ready)
├── 20260430_001_test_recording.py
├── 20260503_001_record_with_label.py
├── 20260504_001_record_stereo.py
└── __init__.py

wavfile/             # Recorded WAV files (auto-created at runtime)
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

## Notes for Future Work

- Pythonista has limited stdlib; test any new packages compatibility
- iOS file permissions require specific handling for ~/Documents access
- Stereo recording uses `AVAudioRecorder` via `objc_util`; mono uses `sound.Recorder`
- Multi-channel (4ch+) requires external USB audio interface + `AVAudioEngine` implementation
- Scripts should print progress/status for user feedback in Pythonista console
