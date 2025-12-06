"""System tray application with menu bar icon."""


import io
import os

import numpy as np
import pystray
from PIL import Image
from pystray import Menu, MenuItem
from reportlab.graphics import renderPM
from svglib.svglib import svg2rlg

from src.logger import get_logger

logger = get_logger(__name__)


class TrayApplication:
    """Menu bar application for TTS controls."""

    def __init__(self):
        """Initialize TrayApplication."""
        logger.info("initializing_tray_app")
        self._is_playing = False
        self._is_paused = False
        self._audio_data: np.ndarray | None = None
        self._sample_rate: int | None = None
        self._icon = None

        # Create menu
        menu = self._create_menu()

        # Create icon (template=True for macOS adaptive menu bar icons)
        icon_image = self._create_icon_image()
        self._icon = pystray.Icon(
            "piper-tts",
            icon_image,
            "Piper TTS Reader",
            menu=menu,
        )
        # Mark as template icon for macOS to auto-invert on dark menu bar
        if hasattr(self._icon, '_icon_class'):
            # pystray on macOS should handle template icons automatically
            pass
        logger.info("tray_app_initialized")

    def _create_icon_image(self) -> Image.Image:
        """Create TTS icon from SVG tropical drink emoji.

        Returns:
            PIL Image for the tray icon (tropical drink with lime and straw)
        """
        # Get path to SVG icon (relative to this file)
        current_dir = os.path.dirname(os.path.abspath(__file__))
        svg_path = os.path.join(os.path.dirname(current_dir), "assets", "icon.svg")

        # Convert SVG to reportlab drawing
        drawing = svg2rlg(svg_path)

        # Render to PNG in memory at menu bar size (44x44 for @2x)
        png_data = io.BytesIO()
        renderPM.drawToFile(drawing, png_data, fmt='PNG', dpi=72, bg=0x00000000)
        png_data.seek(0)

        # Load as PIL Image and resize to exact dimensions
        image = Image.open(png_data)
        image = image.resize((44, 44), Image.Resampling.LANCZOS)

        # Convert to RGBA to ensure transparency
        if image.mode != 'RGBA':
            image = image.convert('RGBA')

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
            MenuItem("Settings", lambda icon, item: self._open_settings(icon, item)),
            MenuItem("Quit", lambda icon, item: self._quit(icon, item)),
        )

    def _has_audio(self) -> bool:
        """Check if audio data is available.

        Returns:
            True if audio is ready for playback/export
        """
        return self._audio_data is not None and self._sample_rate is not None

    def _read_text(self, icon, item):
        """Open input window for text/URL entry.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        logger.info("read_text_clicked")
        # TODO: Open input window
        pass

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
