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

### In Progress 🚧
- 🌐 Extract and read text from URLs
- 📥 Export audio to MP3
- ⌨️ Global keyboard shortcuts
- 🎨 Menu bar UI with system tray icon
- ⚙️ Settings management and persistence

## Requirements

- **macOS** (primary target platform)
- **Python 3.10 - 3.13** (onnxruntime doesn't support 3.14 yet)
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
│   └── ui/                   # UI components (future)
├── tests/
│   ├── test_tts_engine.py
│   ├── test_audio_player.py
│   └── conftest.py
├── voices/                   # Piper voice models (.onnx)
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

- 🚧 **Stage 3**: Text Extraction (Next)
  - URL detection and fetching
  - HTML parsing with BeautifulSoup
  - Content extraction and cleaning

## Testing

All tests use mocking to avoid requiring actual voice files or audio hardware:
- **22 tests total** across both stages
- **87% overall code coverage**
- Tests run in CI on every PR (macOS, Python 3.13)

## CI/CD

GitHub Actions workflow runs on every PR:
- Linting with ruff
- Full test suite
- macOS environment
- Python 3.13

## License

See LICENSE file for details.
