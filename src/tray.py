"""System tray application with menu bar icon."""


import numpy as np
import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem


class TrayApplication:
    """Menu bar application for TTS controls."""

    def __init__(self):
        """Initialize TrayApplication."""
        self._is_playing = False
        self._is_paused = False
        self._speed = 1.0
        self._audio_data: np.ndarray | None = None
        self._sample_rate: int | None = None
        self._icon = None

        # Create menu
        menu = self._create_menu()

        # Create icon
        self._icon = pystray.Icon(
            "piper-tts",
            self._create_icon_image(),
            "Piper TTS Reader",
            menu=menu,
        )

    def _create_icon_image(self) -> Image.Image:
        """Create a simple icon image.

        Returns:
            PIL Image for the tray icon
        """
        # Create a simple 64x64 icon with a speaker symbol
        width = 64
        height = 64
        image = Image.new("RGB", (width, height), "white")
        dc = ImageDraw.Draw(image)

        # Draw a simple speaker shape
        # Rectangle (speaker body)
        dc.rectangle([10, 20, 25, 44], fill="black")
        # Triangle (speaker cone)
        dc.polygon([25, 20, 40, 10, 40, 54, 25, 44], fill="black")
        # Sound waves
        dc.arc([42, 24, 54, 40], start=300, end=60, fill="black", width=2)
        dc.arc([46, 20, 58, 44], start=300, end=60, fill="black", width=2)

        return image

    def _create_menu(self) -> Menu:
        """Create the application menu.

        Returns:
            pystray Menu object
        """
        return Menu(
            MenuItem("Read Text...", self._read_text),
            Menu.SEPARATOR,
            MenuItem(
                "Speed",
                Menu(
                    MenuItem("0.5x", lambda: self._change_speed(None, None, 0.5)),
                    MenuItem("0.75x", lambda: self._change_speed(None, None, 0.75)),
                    MenuItem("1.0x", lambda: self._change_speed(None, None, 1.0)),
                    MenuItem("1.25x", lambda: self._change_speed(None, None, 1.25)),
                    MenuItem("1.5x", lambda: self._change_speed(None, None, 1.5)),
                    MenuItem("2.0x", lambda: self._change_speed(None, None, 2.0)),
                ),
            ),
            MenuItem(
                lambda _: self._get_play_pause_text(),
                self._play_pause,
            ),
            MenuItem("Stop", self._stop),
            MenuItem(
                "Download MP3",
                self._download,
                enabled=self._download_enabled,
            ),
            Menu.SEPARATOR,
            MenuItem("Settings", self._open_settings),
            MenuItem("Quit", self._quit),
        )

    def _get_play_pause_text(self) -> str:
        """Get text for play/pause menu item.

        Returns:
            Menu item text based on current state
        """
        if self._is_paused:
            return "Resume"
        elif self._is_playing:
            return "Pause"
        else:
            return "Play"

    def _has_audio(self) -> bool:
        """Check if audio data is available.

        Returns:
            True if audio is ready for playback/export
        """
        return self._audio_data is not None and self._sample_rate is not None

    def _download_enabled(self, item) -> bool:
        """Check if download should be enabled.

        Args:
            item: pystray MenuItem (unused)

        Returns:
            True if download is available
        """
        return self._has_audio()

    def _read_text(self, icon, item):
        """Open input window for text/URL entry.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        # TODO: Open input window
        pass

    def _change_speed(self, icon, item, speed: float):
        """Change playback speed.

        Args:
            icon: pystray Icon (unused)
            item: pystray MenuItem (unused)
            speed: New speed multiplier
        """
        self._speed = speed
        # TODO: Update audio player speed if playing

    def _play_pause(self, icon, item):
        """Toggle play/pause state.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        if self._is_paused:
            # Resume playback
            self._is_paused = False
            # TODO: Resume audio player
        elif self._is_playing:
            # Pause playback
            self._is_paused = True
            # TODO: Pause audio player
        else:
            # Start playback
            self._is_playing = True
            # TODO: Start audio player

    def _stop(self, icon, item):
        """Stop playback.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        self._is_playing = False
        self._is_paused = False
        # TODO: Stop audio player

    def _download(self, icon, item):
        """Export audio to MP3.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        if not self._has_audio():
            return

        # TODO: Export audio to MP3

    def _open_settings(self, icon, item):
        """Open settings window.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        # TODO: Open settings window
        pass

    def _quit(self, icon, item):
        """Quit the application.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        if self._icon:
            self._icon.stop()

    def run(self):
        """Start the tray application."""
        if self._icon:
            self._icon.run()
