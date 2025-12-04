# Piper TTS Menu Bar Reader

macOS menu bar application for reading text and URLs aloud using Piper TTS.

## Features

### Completed ✓
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
- 📥 MP3 export
  - WAV to MP3 conversion
  - Smart filename generation from text
  - Timestamp-based naming
  - Conflict resolution
- ⌨️ Global keyboard shortcuts
  - System-wide hotkey registration
  - Configurable key bindings
  - Parse "ctrl+shift+p" format
  - Runtime hotkey updates
- 🎨 Menu bar UI with system tray icon
  - pystray-based tray application
  - Speed submenu (0.5x - 2.0x)
  - Dynamic Play/Pause/Resume text
  - Conditional Download menu item
  - Generated speaker icon

### In Progress 🚧
- 🪟 UI Windows (Input and Settings dialogs)

## Requirements

- **macOS** (primary target platform)
- **Python 3.10 - 3.12** (pydub audioop incompatibility with 3.13+)
- **PortAudio** for audio output
- **uv** for package management

## Installation

```bash
# Install system dependencies
brew install portaudio

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project dependencies
uv sync --extra dev
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
piper-tts-chromium-extension/
├── src/
│   ├── tts_engine.py         # Piper TTS wrapper
│   ├── audio_player.py       # Audio playback controller
│   ├── text_extractor.py     # URL and text processing
│   ├── settings.py           # Settings management
│   ├── export.py             # MP3 export functionality
│   └── ui/                   # UI components (future)
├── tests/
│   ├── test_tts_engine.py
│   ├── test_audio_player.py
│   ├── test_text_extractor.py
│   ├── test_settings.py
│   ├── test_export.py
│   └── conftest.py
├── voices/                   # Piper voice models (.onnx)
├── config.json              # User settings (auto-generated)
├── pyproject.toml           # Project metadata and dependencies
└── IMPLEMENTATION_PLAN.md   # Detailed implementation roadmap
```

## Implementation Status

See [IMPLEMENTATION_PLAN.md](IMPLEMENTATION_PLAN.md) for detailed roadmap.

- ✅ **Stage 1**: Project Foundation & TTS Core
  - Project structure with proper packaging
  - PiperTTSEngine class with voice management
  - Speed adjustment and error handling
  - Test suite (8 tests, 94% coverage)

- ✅ **Stage 2**: Audio Playback Controller
  - AudioPlayer class with full controls
  - State management (STOPPED, PLAYING, PAUSED)
  - Thread-safe operations
  - Test suite (13 tests, 83% coverage)

- ✅ **Stage 3**: Text Extraction
  - TextExtractor class with URL detection
  - HTML parsing and content cleaning
  - Whitespace normalization
  - Test suite (8 tests, 95% coverage)

- ✅ **Stage 4**: Settings Management
  - Settings class with JSON persistence
  - Default configuration schema
  - Nested settings access with dot notation
  - Test suite (7 tests, 86% coverage)

- ✅ **Stage 5**: MP3 Export
  - AudioExporter class for WAV to MP3 conversion
  - Smart filename generation with timestamps
  - Conflict resolution for duplicate names
  - Test suite (5 tests, 97% coverage)

- ✅ **Stage 6**: Global Hotkeys
  - HotkeyManager class with pynput integration
  - Hotkey string parsing ("ctrl+shift+p" → pynput format)
  - Register/unregister hotkeys with callbacks
  - Validation for invalid formats
  - Test suite (6 tests, 91% coverage)

- ✅ **Stage 7**: System Tray Integration
  - TrayApplication class with menu bar icon
  - Speed submenu with 6 options (0.5x - 2.0x)
  - Dynamic Play/Pause/Resume menu text
  - Conditional Download MP3 menu item
  - PIL-generated speaker icon
  - Test suite (9 tests, 83% coverage)

- 🚧 **Stage 8**: UI Windows (Next)
  - Input window for text/URL entry
  - Settings window for configuration

## Testing

All tests use mocking to avoid requiring actual voice files or audio hardware:
- **57 tests total** across seven stages
- **88% overall code coverage**
- Tests run in CI on every PR (macOS, Python 3.12)

## CI/CD

GitHub Actions workflow runs on every PR:
- Linting with ruff
- Full test suite
- macOS environment
- Python 3.12

## License

See LICENSE file for details.
