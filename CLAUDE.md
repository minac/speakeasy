# Piper TTS Menu Bar Reader - Project Instructions

## Permissions
- All `git` commands are allowed without confirmation
- All `uv` commands are allowed without confirmation (use `uv sync` for installing dependencies)

## Development Workflow
- Follow TDD: write tests first, then implementation
- Work in feature branches: `cl-<description>`
- Run tests frequently with `uv run pytest`
- Use `ruff` for linting
- Commit with descriptive messages following project conventions

## Architecture Notes

### Core Design Decisions
- **TTS Engine**: Piper TTS for offline, privacy-friendly text-to-speech
  - Why: No API keys, works offline, lightweight, multiple voices
  - Voice models are `.onnx` files + `.json` configs stored in `voices/`
  - Synthesis returns numpy arrays (int16, 22050 Hz sample rate)

- **Audio Playback**: sounddevice + numpy for real-time playback
  - Why: Cross-platform, low-latency, precise control
  - Speed adjustment via scipy's resample (time-domain resampling)
  - Thread-safe state management (STOPPED, PLAYING, PAUSED)
  - Playback runs in separate thread to avoid blocking UI

- **Target Platform**: macOS first (later Linux/Windows)
  - Uses PortAudio backend via sounddevice
  - System requirements: macOS, Python 3.10-3.13, PortAudio

### Module Responsibilities
- `tts_engine.py`: Voice discovery, loading, text→audio synthesis
- `audio_player.py`: Playback control, state management, callbacks
- `text_extractor.py` (future): URL fetching, HTML parsing, content extraction
- `settings.py` (future): JSON persistence, config management
- `ui/` (future): Menu bar tray, input/settings windows

### Testing Strategy
- Mock external dependencies (Piper API, sounddevice, filesystem)
- Unit tests for each module with high coverage (87% overall)
- CI runs on macOS with Python 3.13
- No real voice files needed for tests (all mocked)

### Current Limitations
- No real-time speed change during playback (must restart)
- No streaming synthesis (full text→audio upfront)
- No chunking for long texts (memory constraint risk)
- Audio playback lines 187-227 not fully tested (thread/callback edge cases)

### Next Stage Priorities
1. Text extraction from URLs (Stage 3)
2. Settings persistence (Stage 4)
3. MP3 export functionality (Stage 5)
