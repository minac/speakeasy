# Piper TTS Menu Bar Reader - Implementation Plan

## Overview

A cross-platform menu bar application that reads URLs or text aloud using Piper TTS with playback controls, speed adjustment, and MP3 export functionality.

## Target Features

### Menu Bar Controls (Always Visible)
- **Speed**: Dropdown/slider (0.5x - 2.0x)
- **Play/Pause**: Toggle playback
- **Download**: Export current text as MP3
- **Settings**: Open settings window

### Settings Window
- **Voice Selection**: Dropdown of locally installed Piper voices
- **Keyboard Shortcuts**: Configurable hotkeys for:
  - Play/Pause
  - Stop
  - Speed Up
  - Speed Down
  - Open Input Window
- **Default Speed**: Set default playback speed
- **Output Directory**: Default save location for MP3 files

### Input Methods
- Click tray icon → Input window for URL or text
- Global keyboard shortcut to open input window
- Read from clipboard option

---

## Tech Stack

| Component | Library | Purpose |
|-----------|---------|---------|
| System Tray | `pystray` | Cross-platform menu bar icon |
| GUI | `tkinter` | Settings and input windows |
| TTS Engine | `piper-tts` | Text-to-speech synthesis |
| Web Scraping | `beautifulsoup4`, `requests` | Extract text from URLs |
| Audio Playback | `sounddevice`, `numpy` | Play audio stream |
| MP3 Export | `pydub` | Convert WAV to MP3 |
| Hotkeys | `pynput` | Global keyboard shortcuts |
| Config | `json` | Persist settings |
| Testing | `pytest`, `pytest-mock` | Unit and integration tests |

---

## Project Structure

```
piper-tts-reader/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Application entry point
│   ├── tray.py                 # System tray icon and menu
│   ├── tts_engine.py           # Piper TTS wrapper
│   ├── audio_player.py         # Audio playback controller
│   ├── text_extractor.py       # URL and text processing
│   ├── settings.py             # Settings management
│   ├── hotkeys.py              # Global keyboard shortcuts
│   ├── export.py               # MP3 export functionality
│   └── ui/
│       ├── __init__.py
│       ├── input_window.py     # URL/text input dialog
│       └── settings_window.py  # Settings configuration UI
├── tests/
│   ├── __init__.py
│   ├── test_tts_engine.py
│   ├── test_audio_player.py
│   ├── test_text_extractor.py
│   ├── test_settings.py
│   ├── test_hotkeys.py
│   ├── test_export.py
│   └── conftest.py             # Pytest fixtures
├── voices/                     # Local Piper voice models
├── config.json                 # User settings
├── requirements.txt
├── requirements-dev.txt
├── setup.py
├── README.md
└── IMPLEMENTATION_PLAN.md
```

---

## Development Stages

### Stage 1: Project Foundation & TTS Core ✅
**Goal**: Basic TTS synthesis working from command line

**Status**: COMPLETED

#### 1.1 Project Setup ✅
**Deliverable**: Initialized project with dependencies and test framework

Tasks:
- [x] Create project structure
- [x] Set up `pyproject.toml` with core dependencies (using uv)
- [x] Configure `pytest` with `conftest.py`
- [x] Add `.gitignore`
- [x] Set up GitHub Actions CI

**Tests**:
```python
# test_project_setup.py
def test_imports():
    """Verify all core dependencies are installable"""
    import piper
    import sounddevice
    # Note: pystray, requests, bs4 tested when needed
```

#### 1.2 TTS Engine Wrapper ✅
**Deliverable**: Python class that synthesizes text to audio using Piper

**Implementation**: `src/tts_engine.py` (64 statements, 94% coverage)

Tasks:
- [x] Create `tts_engine.py` with `PiperTTSEngine` class
- [x] Implement voice discovery (scan for .onnx files)
- [x] Implement `synthesize(text) -> audio_data` method
- [x] Implement speed adjustment
- [x] Handle errors gracefully (missing voice, invalid text)

**Tests** (8 tests, all passing):
- test_discover_voices_returns_list
- test_discover_voices_empty_directory
- test_synthesize_returns_audio_data
- test_synthesize_with_speed_adjustment
- test_synthesize_empty_text_raises
- test_synthesize_missing_voice_raises
- test_load_voice_missing_file_raises
- test_get_current_voice

**Key Features**:
- Voice discovery from `voices/` directory
- Automatic config loading (.onnx.json)
- Speed adjustment via scipy.signal.resample
- Returns int16 numpy arrays at 22050 Hz

**Uncovered Lines**: 41-42, 139-140 (CLI entry point, not priority)

---

### Stage 2: Audio Playback Controller ✅
**Goal**: Play, pause, and stop audio with speed control

**Status**: COMPLETED

#### 2.1 Audio Player Implementation ✅
**Deliverable**: Audio player class with full playback controls

**Implementation**: `src/audio_player.py` (118 statements, 83% coverage)

Tasks:
- [x] Create `audio_player.py` with `AudioPlayer` class
- [x] Implement `play(audio_data)` method
- [x] Implement `pause()` / `resume()` methods
- [x] Implement `stop()` method
- [x] Implement real-time speed adjustment
- [x] Add playback state tracking (playing, paused, stopped)
- [x] Implement callback for playback completion

**Tests** (13 tests, all passing):
- test_initial_state_is_stopped
- test_play_starts_playback
- test_pause_stops_playback_temporarily
- test_resume_continues_from_pause_position
- test_stop_resets_position
- test_state_transitions
- test_speed_change_during_playback
- test_play_while_playing_restarts
- test_pause_when_not_playing_does_nothing
- test_resume_when_not_paused_does_nothing
- test_get_position
- test_get_duration

**Key Features**:
- Thread-safe state management (PlaybackState enum)
- Position tracking in samples
- Speed adjustment with automatic resampling
- Completion callbacks
- Playback runs in separate thread

**Uncovered Lines**: 57, 104, 129, 153, 187-194, 208-227
- Mostly thread/callback edge cases and CLI entry point
- Core functionality fully tested

**Known Limitation**: Speed change requires restart (no real-time adjustment during playback)

---

### Stage 3: Text Extraction ✅
**Goal**: Extract readable text from URLs and raw input

**Status**: COMPLETED

#### 3.1 Text Extractor Implementation ✅
**Deliverable**: Module to fetch and clean text from various sources

**Implementation**: `src/text_extractor.py` (37 statements, 95% coverage)

Tasks:
- [x] Create `text_extractor.py` with `TextExtractor` class
- [x] Implement URL detection (is input a URL or plain text?)
- [x] Implement URL fetching with proper headers
- [x] Implement HTML parsing with BeautifulSoup
- [x] Extract main content (remove nav, ads, scripts)
- [x] Clean and normalize text (remove excessive whitespace)
- [x] Handle common errors (404, timeout, invalid URL)
- [x] Support common content types (articles, Wikipedia, docs)

**Tests** (8 tests, all passing):
- test_detect_url_valid
- test_detect_url_plain_text
- test_extract_from_url_returns_text
- test_extract_removes_scripts_and_styles
- test_extract_plain_text_passthrough
- test_extract_url_not_found_raises
- test_extract_timeout_raises
- test_extract_cleans_whitespace

**Key Features**:
- URL detection using urlparse (http/https only)
- Requests.Session with custom User-Agent
- BeautifulSoup HTML parsing
- Removes: script, style, nav, header, footer, aside
- Whitespace normalization with regex
- 30s timeout configurable

**Uncovered Lines**: 39-40 (exception handling edge case)

---

### Stage 4: Settings Management ✅
**Goal**: Persistent configuration with defaults

**Status**: COMPLETED

#### 4.1 Settings Implementation ✅
**Deliverable**: Settings class with JSON persistence

**Implementation**: `src/settings.py` (51 statements, 86% coverage)

Tasks:
- [x] Create `settings.py` with `Settings` class
- [x] Define default settings schema
- [x] Implement load from JSON file
- [x] Implement save to JSON file
- [x] Implement get/set for individual settings
- [x] Create settings on first run with defaults
- [x] Validate settings on load

**Default Settings Schema**:
```json
{
  "voice": "en_US-lessac-medium",
  "speed": 1.0,
  "output_directory": "~/Downloads",
  "shortcuts": {
    "play_pause": "ctrl+shift+p",
    "stop": "ctrl+shift+s",
    "speed_up": "ctrl+shift+]",
    "speed_down": "ctrl+shift+[",
    "open_input": "ctrl+shift+r"
  }
}
```

**Tests** (7 tests, all passing):
- test_load_creates_default_if_missing
- test_load_reads_existing_config
- test_save_writes_to_file
- test_get_returns_value
- test_get_nested_value
- test_set_updates_value
- test_invalid_setting_raises

**Key Features**:
- DEFAULT_SETTINGS with voice, speed, output_directory, shortcuts
- Auto-creates config.json on first run
- Dot notation for nested access ("shortcuts.play_pause")
- KeyError validation for unknown settings
- JSON indent=2 for readability

**Uncovered Lines**: 31, 73, 76, 78, 101, 104, 106 (error message strings)

---

### Stage 5: MP3 Export ✅
**Goal**: Export synthesized audio to MP3 files

**Status**: COMPLETED

#### 5.1 Export Implementation ✅
**Deliverable**: Export module for saving audio as MP3

**Implementation**: `src/export.py` (39 statements, 97% coverage)

Tasks:
- [x] Create `export.py` with `AudioExporter` class
- [x] Implement WAV to MP3 conversion using pydub
- [x] Generate filename from text (first N words + timestamp)
- [x] Use output directory from settings
- [x] Handle filename conflicts
- [x] Return saved file path

**Tests** (5 tests, all passing):
- test_export_creates_mp3_file
- test_export_uses_settings_directory
- test_export_generates_filename
- test_export_handles_filename_conflict
- test_export_returns_file_path

**Key Features**:
- pydub AudioSegment for WAV→MP3 conversion
- Filename: first 5 words + YYYYMMDD_HHMMSS timestamp
- Regex sanitization (alphanumeric + underscore only)
- Conflict resolution with numeric suffixes (_1, _2, etc.)
- Auto-creates output directory with expanduser

**Uncovered Lines**: 112 (infinite loop break condition, unreachable in practice)

---

### Stage 6: Global Hotkeys
**Goal**: System-wide keyboard shortcuts

#### 6.1 Hotkey Implementation
**Deliverable**: Global hotkey listener with configurable bindings

Tasks:
- [ ] Create `hotkeys.py` with `HotkeyManager` class
- [ ] Parse hotkey strings (e.g., "ctrl+shift+p")
- [ ] Register global hotkeys with pynput
- [ ] Implement callback system for hotkey events
- [ ] Support updating hotkeys at runtime
- [ ] Handle platform-specific differences
- [ ] Graceful handling of already-bound shortcuts

**Tests**:
```python
# test_hotkeys.py
class TestHotkeyManager:
    def test_parse_hotkey_string(self):
        """Should parse 'ctrl+shift+p' to key combination"""

    def test_register_hotkey_callback(self):
        """Should register callback for hotkey"""

    def test_unregister_hotkey(self):
        """Should remove hotkey binding"""

    def test_update_hotkey_rebinds(self):
        """Should update existing hotkey binding"""

    def test_invalid_hotkey_raises(self):
        """Should raise for invalid hotkey string"""
```

---

### Stage 7: System Tray Integration
**Goal**: Menu bar icon with controls

#### 7.1 Tray Implementation
**Deliverable**: System tray icon with functional menu

Tasks:
- [ ] Create `tray.py` with `TrayApp` class
- [ ] Create tray icon (use simple icon or generate)
- [ ] Implement menu structure:
  - Speed submenu (0.5x, 0.75x, 1.0x, 1.25x, 1.5x, 2.0x)
  - Play/Pause (dynamic text based on state)
  - Download (disabled when no audio)
  - Settings
  - Quit
- [ ] Connect menu items to callbacks
- [ ] Update menu state dynamically
- [ ] Handle left-click to open input window

**Tests**:
```python
# test_tray.py
class TestTrayApp:
    def test_menu_has_required_items(self):
        """Should have speed, play/pause, download, settings, quit"""

    def test_speed_menu_has_options(self):
        """Should have speed options from 0.5x to 2.0x"""

    def test_play_pause_toggles_text(self):
        """Should show 'Play' when stopped, 'Pause' when playing"""

    def test_download_disabled_when_no_audio(self):
        """Should disable download when nothing to export"""

    def test_left_click_opens_input(self, mock_input_window):
        """Should open input window on left click"""
```

---

### Stage 8: UI Windows
**Goal**: Input and settings windows

#### 8.1 Input Window
**Deliverable**: Dialog for entering URL or text

Tasks:
- [ ] Create `ui/input_window.py` with `InputWindow` class
- [ ] Text area for URL or text input
- [ ] "Read from Clipboard" button
- [ ] "Read" button to start synthesis
- [ ] "Cancel" button
- [ ] Show loading state during URL fetch
- [ ] Display error messages

**Tests**:
```python
# test_input_window.py
class TestInputWindow:
    def test_submit_calls_callback_with_text(self):
        """Should call callback with entered text"""

    def test_clipboard_button_pastes_content(self, mock_clipboard):
        """Should paste clipboard content to text area"""

    def test_cancel_closes_window(self):
        """Should close window without callback"""

    def test_shows_loading_state(self):
        """Should show loading indicator during processing"""
```

#### 8.2 Settings Window
**Deliverable**: Configuration dialog

Tasks:
- [ ] Create `ui/settings_window.py` with `SettingsWindow` class
- [ ] Voice dropdown (populated from discovered voices)
- [ ] Hotkey configuration fields with capture
- [ ] Default speed selector
- [ ] Output directory picker
- [ ] Save and Cancel buttons
- [ ] Validate before saving

**Tests**:
```python
# test_settings_window.py
class TestSettingsWindow:
    def test_voice_dropdown_shows_available_voices(self):
        """Should populate dropdown with discovered voices"""

    def test_hotkey_field_captures_keypress(self):
        """Should capture and display pressed hotkey"""

    def test_save_updates_settings(self):
        """Should save changes to settings"""

    def test_cancel_discards_changes(self):
        """Should close without saving"""

    def test_invalid_hotkey_shows_error(self):
        """Should show error for invalid hotkey"""
```

---

### Stage 9: Integration & Main App
**Goal**: Wire everything together

#### 9.1 Main Application
**Deliverable**: Complete working application

Tasks:
- [ ] Create `main.py` as entry point
- [ ] Initialize all components
- [ ] Wire up event handlers:
  - Tray menu actions
  - Hotkey callbacks
  - Playback state changes
  - Settings updates
- [ ] Implement main read flow:
  1. User inputs URL/text
  2. Extract text
  3. Synthesize with Piper
  4. Play audio
- [ ] Handle errors with user notifications
- [ ] Implement graceful shutdown

**Integration Tests**:
```python
# test_integration.py
class TestIntegration:
    def test_full_read_flow_from_text(self):
        """Should synthesize and play text input"""

    def test_full_read_flow_from_url(self, mock_requests):
        """Should fetch, synthesize, and play URL content"""

    def test_speed_change_affects_playback(self):
        """Should change playback speed when setting changed"""

    def test_download_saves_current_audio(self, tmp_path):
        """Should export current audio to MP3"""

    def test_hotkey_triggers_play_pause(self):
        """Should toggle playback via hotkey"""
```

---

### Stage 10: Polish & Documentation
**Goal**: Production-ready release

#### 10.1 Error Handling & UX
Tasks:
- [ ] Add system notifications for errors
- [ ] Add notification for download complete
- [ ] Handle edge cases (very long text, network issues)
- [ ] Add progress indication for long synthesis
- [ ] Memory optimization for long audio

#### 10.2 Documentation
Tasks:
- [ ] Write comprehensive README.md
- [ ] Document installation steps
- [ ] Document Piper voice installation
- [ ] Add usage examples
- [ ] Document configuration options

#### 10.3 Packaging
Tasks:
- [ ] Create executable with PyInstaller (optional)
- [ ] Test on Linux, macOS, Windows
- [ ] Create release artifacts

---

## Test Strategy

### Unit Tests
- Each module has dedicated test file
- Mock external dependencies (Piper, network, filesystem)
- Target 80%+ code coverage

### Integration Tests
- Test component interactions
- Use fixtures for common setups
- Test full user flows

### Manual Testing Checklist
- [ ] Install on clean system
- [ ] Voice discovery works
- [ ] URL extraction works
- [ ] Playback controls work
- [ ] Speed adjustment works
- [ ] MP3 export works
- [ ] Settings persist across restarts
- [ ] Hotkeys work globally
- [ ] Graceful error handling

---

## Definition of Done (Per Stage)

Each stage is complete when:
1. All tasks checked off
2. All tests passing
3. Code reviewed and clean
4. Feature works end-to-end (CLI or GUI)
5. No regressions in previous stages

---

## Dependencies

### Production
```
piper-tts>=1.2.0
pystray>=0.19.0
Pillow>=9.0.0
sounddevice>=0.4.6
numpy>=1.24.0
requests>=2.28.0
beautifulsoup4>=4.12.0
pydub>=0.25.0
pynput>=1.7.6
```

### Development
```
pytest>=7.0.0
pytest-mock>=3.10.0
pytest-cov>=4.0.0
black>=23.0.0
flake8>=6.0.0
mypy>=1.0.0
```

---

## Getting Started

```bash
# Clone repository
git clone <repo-url>
cd piper-tts-reader

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Linux/macOS
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt
pip install -r requirements-dev.txt

# Install Piper voice (example)
mkdir -p voices
cd voices
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx
wget https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/medium/en_US-lessac-medium.onnx.json
cd ..

# Run tests
pytest

# Run application
python -m src.main
```

---

## Timeline Estimates

> **Note**: Actual timelines depend on developer availability and experience. These stages are designed to produce working software at each step.

| Stage | Description | Complexity |
|-------|-------------|------------|
| 1 | Foundation & TTS Core | Medium |
| 2 | Audio Playback | Medium |
| 3 | Text Extraction | Low |
| 4 | Settings Management | Low |
| 5 | MP3 Export | Low |
| 6 | Global Hotkeys | Medium |
| 7 | System Tray | Medium |
| 8 | UI Windows | Medium |
| 9 | Integration | High |
| 10 | Polish & Docs | Low |

---

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Piper not installed | Clear error message with install instructions |
| No voices available | Guide user to download voices |
| Hotkey conflicts | Allow customization, show conflicts |
| Platform differences | Test on all platforms, use abstractions |
| Long text OOM | Stream synthesis, chunk long texts |
