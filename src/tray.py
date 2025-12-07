"""System tray application with menu bar icon."""


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
        """Create white speaker icon visible on dark menu bar.

        Returns:
            PIL Image for the tray icon (white on transparent)
        """
        # Create 44x44 image for retina displays
        size = 44
        image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(image)

        # Use white color for visibility on dark backgrounds
        color = 'white'

        # Speaker cone (trapezoid on left)
        cone = [(12, 18), (18, 14), (18, 30), (12, 26)]
        draw.polygon(cone, fill=color)

        # Speaker body (small rectangle)
        draw.rectangle([8, 20, 12, 24], fill=color)

        # Sound waves (3 arcs on right side)
        # Wave 1 (closest)
        draw.arc([20, 16, 28, 28], start=300, end=60, fill=color, width=2)

        # Wave 2 (middle)
        draw.arc([24, 13, 32, 31], start=300, end=60, fill=color, width=2)

        # Wave 3 (furthest)
        draw.arc([28, 10, 36, 34], start=300, end=60, fill=color, width=2)

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

    def _read_text(self, icon, item):
        """Open input window for text/URL entry.

        Args:
            icon: pystray Icon
            item: pystray MenuItem
        """
        logger.info("read_text_clicked")
        # TODO: Open input window
        pass

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
