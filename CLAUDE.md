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
- Using Piper TTS for offline text-to-speech
- Cross-platform menu bar app (macOS, Linux, Windows)
- Local voice models stored in `voices/` directory
- Settings persisted in `config.json`
