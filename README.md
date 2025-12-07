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

Download voice models from [Piper TTS releases](https://github.com/rhasspy/piper/releases) and place them in the `voices/` directory:

```bash
# Create voices directory
mkdir -p voices

# Example: Download a voice model
cd voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/v1.0.0/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
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
│   ├── main.py              # Application entry point & coordinator
│   ├── logger.py            # Structured logging
│   ├── tts_engine.py        # Piper TTS wrapper
│   ├── audio_player.py      # Audio playback controller
│   ├── text_extractor.py    # URL and text processing
│   ├── settings.py          # Settings management
│   ├── hotkeys.py           # Global keyboard shortcuts
│   ├── tray.py              # System tray application
│   └── ui/
│       ├── input_window.py  # Text/URL input dialog
│       └── settings_window.py # Configuration dialog
├── tests/
│   ├── test_tts_engine.py
│   ├── test_audio_player.py
│   ├── test_text_extractor.py
│   ├── test_settings.py
│   ├── test_hotkeys.py
│   ├── test_tray.py
│   ├── test_input_window.py
│   ├── test_settings_window.py
│   └── conftest.py
├── assets/
│   └── icon.svg             # Menu bar icon (SVG)
├── voices/                  # Piper voice models (.onnx)
├── config.json             # User settings (auto-generated)
├── pyproject.toml          # Project metadata and dependencies
├── CLAUDE.md               # Project instructions for Claude
└── IMPLEMENTATION_PLAN.md  # Detailed implementation roadmap
```

## CI/CD

GitHub Actions workflow runs on every PR:
- Linting with ruff
- Full test suite
- macOS environment
- Python 3.12

## License

See LICENSE file for details.
