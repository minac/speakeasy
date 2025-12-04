# Piper TTS Menu Bar Reader - Project Instructions

## Permissions
- All `git` commands are allowed without confirmation (checkout, add, commit, push, pull, branch, merge)
- All `gh` commands are allowed without confirmation (pr create, pr edit)
- All `uv` commands are allowed without confirmation (sync, run pytest, run ruff)
- File operations (Read, Write, Edit) allowed without confirmation

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
  - System requirements: macOS, Python 3.10-3.12, PortAudio
  - Python 3.13+ not supported due to pydub/audioop incompatibility

### Module Responsibilities
- `tts_engine.py`: Voice discovery, loading, text→audio synthesis
- `audio_player.py`: Playback control, state management, callbacks
- `text_extractor.py`: URL fetching, HTML parsing, content extraction
- `settings.py`: JSON persistence, config management with dot notation
- `export.py`: WAV to MP3 conversion, filename generation
- `hotkeys.py`: Global keyboard shortcuts with pynput
- `tray.py`: System tray icon with menu (pystray + PIL)
- `ui/input_window.py`: Text/URL input dialog (tkinter)
- `ui/settings_window.py`: Configuration dialog (tkinter/ttk)

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

**Global Hotkeys**:
- pynput GlobalHotKeys for system-wide shortcuts
- Parses "ctrl+shift+p" format to pynput format
- Dynamic registration/unregistration with listener rebuild
- Validates hotkey format (empty, no key, invalid modifiers)

**System Tray**:
- pystray for menu bar icon
- PIL-generated speaker icon (64x64)
- Dynamic menu text (Play/Pause/Resume)
- Speed submenu (6 options: 0.5x - 2.0x)
- Conditional Download menu item

**UI Windows**:
- tkinter/ttk for input and settings dialogs
- InputWindow: text area, clipboard paste, Read/Cancel buttons
- SettingsWindow: voice dropdown, speed scale, directory picker

### Testing Strategy
- Mock external dependencies (Piper API, sounddevice, filesystem, network, pynput, pystray, tkinter)
- Unit tests for each module with high coverage (90% overall)
- 74 tests across 8 stages
- CI runs on macOS with Python 3.12
- No real voice files, network calls, audio hardware, or GUI needed

### Current Limitations
- No real-time speed change during playback (must restart)
- No streaming synthesis (full text→audio upfront)
- No chunking for long texts (memory constraint risk)
- Audio playback lines 187-227 not fully tested (thread/callback edge cases)
- Python 3.13+ not supported (pydub requires audioop, removed in 3.13)

### Completed Stages
- ✅ Stage 1: TTS Core (PiperTTSEngine)
- ✅ Stage 2: Audio Playback (AudioPlayer)
- ✅ Stage 3: Text Extraction (TextExtractor)
- ✅ Stage 4: Settings Management (Settings)
- ✅ Stage 5: MP3 Export (AudioExporter)
- ✅ Stage 6: Global Hotkeys (HotkeyManager)
- ✅ Stage 7: System Tray (TrayApplication)
- ✅ Stage 8: UI Windows (InputWindow, SettingsWindow)

### Next Stage Priorities
1. Integration & Main App (Stage 9) - Wire all components together
2. Manual Testing & Polish (Stage 10) - End-to-end testing, bug fixes
