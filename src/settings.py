"""Settings management with JSON persistence."""

import json
from pathlib import Path
from typing import Any


class Settings:
    """Manage application settings with JSON persistence."""

    DEFAULT_SETTINGS = {
        "voice": "en_US-lessac-medium",
        "speed": 1.0,
        "output_directory": "~/Downloads",
        "shortcuts": {
            "play_pause": "ctrl+shift+p",
            "stop": "ctrl+shift+s",
            "speed_up": "ctrl+shift+]",
            "speed_down": "ctrl+shift+[",
            "open_input": "ctrl+shift+r",
        },
    }

    def __init__(self, config_path: Path | str | None = None):
        """Initialize Settings.

        Args:
            config_path: Path to config file. Defaults to config.json in current dir.
        """
        if config_path is None:
            config_path = Path.cwd() / "config.json"
        self.config_path = Path(config_path)
        self._settings = self._load()

    def _load(self) -> dict:
        """Load settings from file or create defaults.

        Returns:
            Settings dictionary
        """
        if self.config_path.exists():
            with open(self.config_path) as f:
                return json.load(f)
        else:
            # Create defaults
            settings = self.DEFAULT_SETTINGS.copy()
            self._settings = settings
            self.save()
            return settings

    def save(self) -> None:
        """Persist settings to JSON file."""
        with open(self.config_path, "w") as f:
            json.dump(self._settings, f, indent=2)

    def get(self, key: str) -> Any:
        """Get setting value.

        Args:
            key: Setting key, supports dot notation for nested values (e.g., "shortcuts.play_pause")

        Returns:
            Setting value

        Raises:
            KeyError: If key does not exist
        """
        if "." in key:
            # Nested key
            parts = key.split(".", 1)
            parent_key, child_key = parts[0], parts[1]
            if parent_key not in self._settings:
                raise KeyError(f"Setting key not found: {parent_key}")
            parent = self._settings[parent_key]
            if not isinstance(parent, dict):
                raise KeyError(f"Setting key is not nested: {parent_key}")
            if child_key not in parent:
                raise KeyError(f"Setting key not found: {key}")
            return parent[child_key]
        else:
            # Top-level key
            if key not in self._settings:
                raise KeyError(f"Setting key not found: {key}")
            return self._settings[key]

    def set(self, key: str, value: Any) -> None:
        """Set setting value.

        Args:
            key: Setting key, supports dot notation for nested values (e.g., "shortcuts.play_pause")
            value: New value

        Raises:
            KeyError: If key does not exist
        """
        if "." in key:
            # Nested key
            parts = key.split(".", 1)
            parent_key, child_key = parts[0], parts[1]
            if parent_key not in self._settings:
                raise KeyError(f"Setting key not found: {parent_key}")
            parent = self._settings[parent_key]
            if not isinstance(parent, dict):
                raise KeyError(f"Setting key is not nested: {parent_key}")
            if child_key not in parent:
                raise KeyError(f"Setting key not found: {key}")
            parent[child_key] = value
        else:
            # Top-level key
            if key not in self._settings:
                raise KeyError(f"Setting key not found: {key}")
            self._settings[key] = value
