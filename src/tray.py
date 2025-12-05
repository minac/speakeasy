"""System tray application with menu bar icon."""


import numpy as np
import pystray
from PIL import Image, ImageDraw
from pystray import Menu, MenuItem

from src.logger import get_logger

logger = get_logger(__name__)


class TrayApplication:
    """Menu bar application for TTS controls."""

    def __init__(self):
        """Initialize TrayApplication."""
        logger.info("initializing_tray_app")
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
        logger.info("tray_app_initialized")

    def _create_icon_image(self) -> Image.Image:
        """Create a colorful icon image for macOS menu bar (like Tot).

        Returns:
            PIL Image for the tray icon (colorful, visible on any background)
        """
        # Create a 22x22 icon (standard macOS menu bar size)
        width = 22
        height = 22
        image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
        dc = ImageDraw.Draw(image)

        # Colorful circular icon with blue/gradient (like Tot)
        # Main circle - bright blue
        dc.ellipse([3, 3, 19, 19], fill="#007AFF", outline="#0051D5")

        # Simple speaker/sound icon inside
        # Speaker body (white)
        dc.rectangle([7, 9, 9, 13], fill="white")
        # Speaker cone (white triangle)
        dc.polygon([9, 9, 12, 7, 12, 15, 9, 13], fill="white")
        # Sound waves (white)
        dc.arc([13, 8, 15, 10], start=270, end=90, fill="white", width=1)
        dc.arc([14, 7, 16, 11], start=270, end=90, fill="white", width=1)

        return image

    def _create_menu(self) -> Menu:
        """Create the application menu.

        Returns:
            pystray Menu object

        Note:
            We use lambdas to wrap method calls so that when main.py replaces
            the methods (e.g., self._read_text = ...), the menu items will
            call the new implementations. Without lambdas, the menu would
            hold direct references to the original stub methods.
        """
        return Menu(
            MenuItem("Read Text...", lambda icon, item: self._read_text(icon, item)),
            Menu.SEPARATOR,
            MenuItem(
                "Speed",
                Menu(
                    MenuItem(
                        lambda _: "✓ 0.5x" if self._speed == 0.5 else "0.5x",
                        lambda: self._change_speed(None, None, 0.5),
                    ),
                    MenuItem(
                        lambda _: "✓ 0.75x" if self._speed == 0.75 else "0.75x",
                        lambda: self._change_speed(None, None, 0.75),
                    ),
                    MenuItem(
                        lambda _: "✓ 1.0x" if self._speed == 1.0 else "1.0x",
                        lambda: self._change_speed(None, None, 1.0),
                    ),
                    MenuItem(
                        lambda _: "✓ 1.25x" if self._speed == 1.25 else "1.25x",
                        lambda: self._change_speed(None, None, 1.25),
                    ),
                    MenuItem(
                        lambda _: "✓ 1.5x" if self._speed == 1.5 else "1.5x",
                        lambda: self._change_speed(None, None, 1.5),
                    ),
                    MenuItem(
                        lambda _: "✓ 2.0x" if self._speed == 2.0 else "2.0x",
                        lambda: self._change_speed(None, None, 2.0),
                    ),
                ),
            ),
            MenuItem(
                "Download MP3",
                lambda icon, item: self._download(icon, item),
                enabled=self._download_enabled,
            ),
            Menu.SEPARATOR,
            MenuItem("Settings", lambda icon, item: self._open_settings(icon, item)),
            MenuItem("Quit", lambda icon, item: self._quit(icon, item)),
        )

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
        logger.info("read_text_clicked")
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
        """Start playback.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        logger.info("play_clicked")
        self._is_playing = True
        self._is_paused = False
        logger.info("starting_playback")
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
        logger.info("settings_clicked")
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
        """Start the tray application (blocking).

        This blocks the calling thread. On macOS, this must be called
        from the main thread as it uses NSApplication internally.
        """
        logger.info("starting_tray_icon")
        if self._icon:
            self._icon.run()
        logger.info("tray_icon_stopped")

    def run_detached(self):
        """Start the tray application in detached mode.

        This is required on macOS when integrating with another mainloop
        (e.g., tkinter). It allows pystray to run alongside the other
        framework's event loop without blocking.

        See: https://pystray.readthedocs.io/en/latest/reference.html
        """
        logger.info("starting_tray_icon_detached")
        if self._icon:
            self._icon.run_detached()
        logger.debug("tray_icon_running_detached")

    def stop(self):
        """Stop the tray application.

        This can be called from any thread to stop the icon.
        """
        logger.info("stopping_tray_icon")
        if self._icon:
            self._icon.stop()
        logger.debug("tray_icon_stop_requested")
