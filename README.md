# Speakeasy

macOS menu bar application for reading text and URLs aloud using Piper TTS.

## Features

- 🎙️ Offline text-to-speech using Piper TTS
  - Voice discovery from local `.onnx` files
  - Speed adjustment (0.5x - 2.0x)
  - WAV audio synthesis
- ⚡ Audio playback controls
  - Play, pause, resume, stop
  - Real-time speed adjustment
  - Position and duration tracking
  - Playback state management
  - Completion callbacks
- 🌐 Text extraction from URLs
  - URL detection with protocol validation
  - HTTP fetching with proper headers
  - HTML parsing and content cleaning
  - Whitespace normalization
  - Plain text passthrough
- ⚙️ Settings management
  - JSON persistence with defaults
  - Nested settings with dot notation
  - Voice, speed, output directory, shortcuts
- ⌨️ Global keyboard shortcuts
  - System-wide hotkey registration
  - Configurable key bindings
  - Parse "ctrl+shift+p" format
  - Runtime hotkey updates
- 🎨 Menu bar UI with system tray icon
  - pystray-based tray application
  - Simple menu with Read Text, Settings, and Quit
  - SVG icon with macOS template support (auto-inverts on dark menu bar)
- 🪟 UI Windows
  - Input window for text/URL entry
  - Settings window for configuration
  - tkinter/ttk-based dialogs
- 🔗 Full application integration
  - All components wired together
  - Event-driven architecture
  - Settings persistence
  - Hotkey bindings

## Requirements

- **macOS** (primary target platform)
- **Python 3.10 - 3.12** (recommended)
- **PortAudio** for audio output
- **uv** for package management
- **Piper voice models** (.onnx files)

## Installation

### 1. Install System Dependencies

```bash
# Install PortAudio
brew install portaudio

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 2. Clone and Install Project

```bash
# Clone repository
git clone https://github.com/minac/speakeasy.git
cd speakeasy

# Install Python dependencies
uv sync --extra dev
```

### 3. Download Piper Voice Models

Download voice models from [Piper Huggingface](https://huggingface.co/rhasspy/piper-voices/tree/main)) and place them in the `voices/` directory:

```bash
# Create voices directory
mkdir -p voices

# Example: Download a voice model
cd voices
curl -L -o en_US-lessac-high.onnx https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/high/en_US-lessac-high.onnx
curl -L -o en_US-lessac-high.onnx.json https://huggingface.co/rhasspy/piper-voices/blob/main/en/en_US/lessac/high/en_US-lessac-high.onnx.json
cd ..
```

## Running the Application

### Step-by-Step Guide

1. **Ensure voice models are installed** in the `voices/` directory
2. **Run the application**:
   ```bash
   uv run python -m src.main
   ```
3. **Look for the speaker icon** in your macOS menu bar (top-right)
4. **Click the icon** to access the menu

## Building for macOS (Optional)

> **Note**: The PyInstaller build configuration (`speakeasy.spec` and `build_app.sh`) was previously created but has been removed from the repository. You can restore these files from git history (commit `d1916e2`) if you need to create a standalone macOS app bundle.

The build would create a standalone `.app` bundle that:
- Runs in the background (no Dock icon, menu bar only)
- Self-contained with all dependencies
- Can be added to Login Items for auto-start
- Works like any native macOS app

### To Restore Build Files

```bash
# Restore from git history
git show d1916e2:speakeasy.spec > speakeasy.spec
git show d1916e2:build_app.sh > build_app.sh
chmod +x build_app.sh

# Build the app
./build_app.sh
```

### Alternative: Run from Source

For development and testing, running from source is simpler:

```bash
uv run python -m src.main
```

## Development

```bash
# Run tests
uv run pytest -v

# Run tests with coverage
uv run pytest --cov=src --cov-report=term-missing

# Lint code
uv run ruff check src/ tests/

# Auto-fix linting issues
uv run ruff check --fix src/ tests/
```

## Project Structure

```
speakeasy/
├── src/
│   ├── main.py              # Application entry point & coordinator (148 lines, 0% test coverage)
│   ├── logger.py            # Structured logging (8 lines, 75% coverage)
│   ├── tts_engine.py        # Piper TTS wrapper (70 lines, 90% coverage)
│   ├── audio_player.py      # Audio playback controller (144 lines, 82% coverage)
│   ├── text_extractor.py    # URL and text processing (37 lines, 95% coverage)
│   ├── settings.py          # Settings management (51 lines, 86% coverage)
│   ├── hotkeys.py           # Global keyboard shortcuts (55 lines, 91% coverage)
│   ├── tray.py              # System tray application (53 lines, 77% coverage)
│   └── ui/
│       ├── input_window.py  # Text/URL input dialog (92 lines, 75% coverage)
│       └── settings_window.py # Configuration dialog (91 lines, 93% coverage)
├── tests/                   # 65 tests across 8 test modules
│   ├── test_tts_engine.py   # 8 tests
│   ├── test_audio_player.py # 13 tests
│   ├── test_text_extractor.py # 8 tests
│   ├── test_settings.py     # 7 tests
│   ├── test_hotkeys.py      # 6 tests
│   ├── test_tray.py         # 5 tests
│   ├── test_input_window.py # 8 tests
│   ├── test_settings_window.py # 9 tests
│   └── conftest.py          # Test fixtures
├── assets/
│   ├── icon.svg             # Menu bar icon (SVG)
│   ├── icon.png             # PNG version (44x44 @2x)
│   └── icon.icns            # macOS icon for app bundle
├── voices/                  # Piper voice models (.onnx + .json)
├── config.json              # User settings (auto-generated)
├── pyproject.toml           # Project metadata and dependencies
├── CLAUDE.md                # Project instructions for Claude Code
└── README.md                # This file
```

## Test Coverage

Overall: **68%** (749 statements, 238 missed)

| Module | Coverage | Notes |
|--------|----------|-------|
| text_extractor.py | 95% | Highest coverage |
| settings_window.py | 93% | Nearly complete |
| hotkeys.py | 91% | Excellent |
| tts_engine.py | 90% | Core functionality well-tested |
| settings.py | 86% | Good coverage |
| audio_player.py | 82% | Some threading edge cases uncovered |
| tray.py | 77% | Basic functionality covered |
| input_window.py | 75% | UI interactions partially tested |
| logger.py | 75% | Minimal module, well-covered |
| main.py | 0% | Integration layer untested |

## CI/CD

GitHub Actions workflow runs on every PR:
- Linting with ruff
- Full test suite
- macOS environment
- Python 3.12

## License

See LICENSE file for details.
