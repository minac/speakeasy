"""Tests for Settings class."""

import json

import pytest

from src.settings import Settings


class TestSettings:
    """Test suite for Settings."""

    def test_load_creates_default_if_missing(self, tmp_path):
        """Should create config with defaults if not exists."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        # Config file should be created
        assert config_file.exists()

        # Should have default values
        assert settings.get("voice") == "en_US-lessac-medium"
        assert settings.get("speed") == 1.0
        assert settings.get("output_directory") == "~/Downloads"
        assert "play_pause" in settings.get("shortcuts")

    def test_load_reads_existing_config(self, tmp_path):
        """Should load existing configuration."""
        config_file = tmp_path / "config.json"
        config_data = {
            "voice": "custom-voice",
            "speed": 1.5,
            "output_directory": "~/Music",
            "shortcuts": {
                "play_pause": "ctrl+alt+p",
                "stop": "ctrl+alt+s",
                "speed_up": "ctrl+alt+]",
                "speed_down": "ctrl+alt+[",
                "open_input": "ctrl+alt+r",
            },
        }
        config_file.write_text(json.dumps(config_data, indent=2))

        settings = Settings(config_path=config_file)

        assert settings.get("voice") == "custom-voice"
        assert settings.get("speed") == 1.5
        assert settings.get("output_directory") == "~/Music"
        assert settings.get("shortcuts.play_pause") == "ctrl+alt+p"

    def test_save_writes_to_file(self, tmp_path):
        """Should persist settings to JSON."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        settings.set("voice", "new-voice")
        settings.set("speed", 2.0)
        settings.save()

        # Read file directly
        saved_data = json.loads(config_file.read_text())
        assert saved_data["voice"] == "new-voice"
        assert saved_data["speed"] == 2.0

    def test_get_returns_value(self, tmp_path):
        """Should return setting value."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        assert settings.get("voice") == "en_US-lessac-medium"
        assert settings.get("speed") == 1.0

    def test_get_nested_value(self, tmp_path):
        """Should return nested setting like shortcuts.play_pause."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        assert settings.get("shortcuts.play_pause") == "ctrl+shift+p"
        assert settings.get("shortcuts.stop") == "ctrl+shift+s"
        assert settings.get("shortcuts.speed_up") == "ctrl+shift+]"

    def test_set_updates_value(self, tmp_path):
        """Should update setting value."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        settings.set("voice", "updated-voice")
        assert settings.get("voice") == "updated-voice"

        settings.set("shortcuts.play_pause", "ctrl+alt+p")
        assert settings.get("shortcuts.play_pause") == "ctrl+alt+p"

    def test_invalid_setting_raises(self, tmp_path):
        """Should raise for unknown setting key."""
        config_file = tmp_path / "config.json"
        settings = Settings(config_path=config_file)

        with pytest.raises(KeyError):
            settings.get("nonexistent_key")

        with pytest.raises(KeyError):
            settings.set("nonexistent_key", "value")
