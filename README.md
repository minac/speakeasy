# Piper TTS Menu Bar Reader

macOS menu bar application for reading text and URLs aloud using Piper TTS.

## Features (In Progress)

- 🎙️ Offline text-to-speech using Piper TTS
- ⚡ Playback controls (play, pause, speed adjustment)
- 📥 Export audio to MP3
- ⌨️ Global keyboard shortcuts
- 🌐 Extract and read text from URLs

## Requirements

- macOS
- Python 3.10+
- PortAudio (`brew install portaudio`)

## Development

```bash
# Install dependencies
brew install portaudio
uv sync --extra dev

# Run tests
uv run pytest

# Lint
uv run ruff check
```

## Project Status

Stage 1: Project Foundation & TTS Core ✓
Stage 2: Audio Playback Controller ✓
