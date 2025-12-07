# Speakeasy - Project Instructions

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
- `main.py`: Application coordinator (PiperTTSApp), wires all components together
- `logger.py`: Structured logging with context fields
- `tts_engine.py`: Voice discovery, loading, text→audio synthesis
- `audio_player.py`: Playback control, state management, callbacks
- `text_extractor.py`: URL fetching, HTML parsing, content extraction
- `settings.py`: JSON persistence, config management with dot notation
- `hotkeys.py`: Global keyboard shortcuts with pynput
- `tray.py`: System tray icon with menu (pystray + svglib for SVG icon)
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

**Global Hotkeys**:
- pynput GlobalHotKeys for system-wide shortcuts
- Parses "ctrl+shift+p" format to pynput format
- Dynamic registration/unregistration with listener rebuild
- Validates hotkey format (empty, no key, invalid modifiers)

**System Tray**:
- pystray for menu bar icon
- SVG icon (assets/icon.svg) loaded via svglib + reportlab, rendered at 44x44 @2x for retina
- macOS template icon support (auto-inverts on dark menu bar)
- Simple static menu: Read Text, Settings, Quit
- Note: Playback controls (Play/Pause/Stop) are in InputWindow, NOT tray menu

**UI Windows**:
- tkinter/ttk for input and settings dialogs
- InputWindow: text area, Play/Stop buttons, clipboard paste
  - Requires 2 callbacks: `callback` (text submission), `stop_callback`
  - Play button becomes Stop button when audio is playing
- SettingsWindow: voice dropdown, speed scale, directory picker

**Logging**:
- Structured logging via logger.py
- Context fields (e.g., voice_name, speed, text_length)
- Log levels: DEBUG for detailed flow, INFO for key events
- Integration throughout all modules

### Testing Strategy
- Mock external dependencies (Piper API, sounddevice, filesystem, network, pynput, pystray, tkinter)
- Unit tests for each module with high coverage (core modules 72-95%)
- 66 tests total across all modules (removed export tests)
- CI runs on macOS with Python 3.12 via GitHub Actions
- No real voice files, network calls, audio hardware, or GUI needed
- Zero test dependencies on external resources

### Current Limitations
- No real-time speed change during playback (must restart playback)
- No streaming synthesis (full text→audio upfront)
- No chunking for long texts (memory constraint risk for very large documents)
- No MP3 export functionality (removed for simplicity)
- Main integration layer (main.py) not tested (0% coverage)
- Some edge cases in audio playback threading/callbacks not fully covered
- Windows/Linux support untested (macOS-first development)

### Completed Stages
- ✅ Stage 1: TTS Core (PiperTTSEngine) - 8 tests, 91% coverage
- ✅ Stage 2: Audio Playback (AudioPlayer) - 13 tests, 82% coverage
- ✅ Stage 3: Text Extraction (TextExtractor) - 8 tests, 95% coverage
- ✅ Stage 4: Settings Management (Settings) - 7 tests, 86% coverage
- ✅ Stage 5: Global Hotkeys (HotkeyManager) - 6 tests, 91% coverage
- ✅ Stage 6: System Tray (TrayApplication) - 6 tests, 74% coverage
- ✅ Stage 7: UI Windows (InputWindow, SettingsWindow) - 17 tests, 72-93% coverage
- ✅ Stage 8: Integration & Main App (PiperTTSApp) - main.py complete, 0% test coverage
- ✅ Bug Fix: Wire InputWindow callbacks (PR #25) - Stop button now functional
- ✅ Simplification: Remove MP3 export feature - Removed export module, pydub dependency

### Known Issues & Quirks
- **InputWindow callbacks**: Must pass 2 callbacks (callback, stop_callback) when creating InputWindow in main.py
- **Tray menu**: Simple static menu only - playback controls are in InputWindow UI, not tray
- **macOS hotkeys**: Disabled due to pynput/pystray/tkinter threading conflicts (see main.py comments)

### Next Priorities
1. **Manual Testing & Polish** - End-to-end testing with real voice files
2. **Integration Tests** - Test main.py coordinator with integrated components
3. **Bug Fixes** - Address issues found during manual testing
4. **Performance** - Optimize for large texts, reduce memory usage
5. **Cross-platform** - Test on Linux/Windows, fix platform-specific issues
