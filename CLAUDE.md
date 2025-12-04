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
- `text_extractor.py`: URL fetching, HTML parsing, content extraction
- `settings.py`: JSON persistence, config management with dot notation
- `export.py`: WAV to MP3 conversion, filename generation
- `ui/` (future): Menu bar tray, input/settings windows

### Implementation Details

**Text Extraction**:
- BeautifulSoup for HTML parsing
- Removes scripts, styles, nav, headers, footers
- Regex-based whitespace normalization
- 30s timeout for HTTP requests
- Custom User-Agent headers

**Settings Management**:
- JSON file persistence (config.json)
- Default schema: voice, speed, output_directory, shortcuts
- Dot notation for nested access (e.g., "shortcuts.play_pause")
- KeyError validation for unknown settings

**MP3 Export**:
- pydub for WAV→MP3 conversion
- Filename: first 5 words + timestamp
- Conflict resolution with numeric suffixes
- Auto-creates output directory

### Testing Strategy
- Mock external dependencies (Piper API, sounddevice, filesystem, network)
- Unit tests for each module with high coverage (89% overall)
- CI runs on macOS with Python 3.13
- No real voice files, network calls, or audio hardware needed

### Current Limitations
- No real-time speed change during playback (must restart)
- No streaming synthesis (full text→audio upfront)
- No chunking for long texts (memory constraint risk)
- Audio playback lines 187-227 not fully tested (thread/callback edge cases)
- pydub warning about deprecated audioop module (Python 3.13+)

### Next Stage Priorities
1. Global keyboard shortcuts (Stage 6)
2. System tray integration (Stage 7)
3. UI windows for input/settings (Stage 8)
