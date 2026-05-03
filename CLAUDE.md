# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**LearningAcoustics** is a Pythonista-based audio recording and processing project designed to run on iOS devices through the Pythonista app and Working Copy integration. The primary workflow involves developing audio capture and analysis tools that execute directly on iOS.

## Development Workflow

### Branch Strategy
- **Development branch**: `claude/test-pythonista-push-vmtde`
- All development and commits should go to this branch
- Push changes with: `git push -u origin claude/test-pythonista-push-vmtde`
- Tested via Working Copy on iOS before finalizing

### Architecture

The project follows a clear separation of concerns:

```
tools/               # Reusable modules and functions
├── recording.py     # Audio capture functionality
└── __init__.py

src/                 # Execution scripts (iOS ready)
├── 20260430_001_test_recording.py
└── __init__.py
```

### Key Principles

1. **tools/** folder contains:
   - Reusable functions and classes
   - Pythonista-compatible iOS API wrappers
   - Imported by src/ scripts and external code

2. **src/** folder contains:
   - Executable scripts that can be run directly in Pythonista
   - Naming convention: `YYYYMMDD_001_content_description.py`
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
python3 src/20260430_001_test_recording.py
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

1. Push changes to `claude/test-pythonista-push-vmtde`
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
git push -u origin claude/test-pythonista-push-vmtde

# View recent commits
git log --oneline -5
```

## File Structure Guidelines

- **New tools**: Add to `tools/` with descriptive names, then import in `tools/__init__.py`
- **New scripts**: Create in `src/` with format `YYYYMMDD_NNN_description.py`
- **Dependencies**: Declare in `Pipfile` if adding external packages

## Testing on iOS

1. Code must work within Pythonista's sandbox
2. All file I/O should target `~/Documents` directory
3. Test by running directly in Pythonista via Working Copy
4. Verify output files appear in Documents folder

## Pythonista Audio Recording

The project uses Pythonista's built-in `sound.Recorder` class for audio recording. This approach is more reliable than direct AVFoundation calls in Pythonista's environment:

```python
import sound
recorder = sound.Recorder(filepath)
recorder.record()
# ... wait for duration ...
recorder.stop()
# File is automatically saved to filepath
```

Benefits:
- Built-in Pythonista class with consistent API
- Handles audio session setup automatically
- Automatically saves to specified file path
- Better compatibility across Pythonista versions

## WAV File Saving Convention

### Save Location

All WAV recordings are saved to:
```
~/Documents/wavfile/
```

This folder is created automatically at runtime if it does not exist.

### File Naming Format

```
YYYYMMDD_HHMMSS_<label>.wav
```

- `YYYYMMDD` — Recording date (e.g. `20260503`)
- `HHMMSS`   — Recording start time (e.g. `143022`)
- `<label>`  — User-supplied label entered in a popup dialog each time

Example: `20260503_143022_cat.wav`

### Label Input (Popup Dialog)

Use `tools.record_with_label()` (or run `src/20260503_001_record_with_label.py`) to trigger a Pythonista popup (`dialogs.input_alert`) that asks for a label before each recording. The label becomes the `XX` part of the filename. Spaces are replaced with underscores; empty input defaults to `noname`.

```python
from tools import record_with_label
path = record_with_label(duration=5)
```

## Notes for Future Work

- Pythonista has limited stdlib; test any new packages compatibility
- iOS file permissions require specific handling for ~/Documents access
- Use `sound` module instead of direct framework calls for audio operations
- Scripts should print progress/status for user feedback in Pythonista console
