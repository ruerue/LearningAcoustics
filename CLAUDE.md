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
- Use `objc` for iOS API access (AVFoundation, etc.)
- Assume `sys.path` includes the parent directory for importing tools/
- Path handling: Use `os.path.expanduser('~/Documents')` for file storage
- All imports should handle Pythonista's limited stdlib gracefully

Example execution:
```bash
# From Pythonista or terminal
python3 src/20260430_001_test_recording.py
```

### Working Copy Workflow

1. Push changes to `claude/test-pythonista-push-vmtde`
2. Pull in Working Copy on iOS
3. Open script in Pythonista from Working Copy
4. Run and verify functionality
5. If working, commit with clear messages

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

## Notes for Future Work

- Pythonista has limited stdlib; test any new packages compatibility
- iOS file permissions require specific handling for ~/Documents access
- AVFoundation requires proper audio session setup (see `tools/recording.py` example)
- Scripts should print progress/status for user feedback in Pythonista console
