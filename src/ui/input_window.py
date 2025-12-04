"""Input window for entering text or URLs."""

import tkinter as tk
from collections.abc import Callable

from src.logger import get_logger

logger = get_logger(__name__)


class InputWindow:
    """Dialog for text or URL input."""

    def __init__(self, callback: Callable[[str], None]):
        """Initialize InputWindow.

        Args:
            callback: Function to call with submitted text
        """
        logger.info("creating_input_window")
        self._callback = callback
        self._window = tk.Toplevel()
        self._window.title("Piper TTS Reader")
        self._window.geometry("600x400")
        self._window.lift()
        self._window.attributes('-topmost', True)
        self._window.after_idle(self._window.attributes, '-topmost', False)

        # Create UI elements
        self._create_widgets()
        logger.debug("input_window_created")

    def _create_widgets(self):
        """Create all window widgets."""
        # Instructions label
        instructions = tk.Label(
            self._window,
            text="Enter text or paste a URL to read aloud:",
            pady=10,
        )
        instructions.pack()

        # Text area
        self._text_area = tk.Text(
            self._window,
            wrap=tk.WORD,
            width=70,
            height=15,
        )
        self._text_area.pack(padx=10, pady=10, expand=True, fill=tk.BOTH)

        # Button frame
        button_frame = tk.Frame(self._window)
        button_frame.pack(pady=10)

        # Paste from Clipboard button
        paste_btn = tk.Button(
            button_frame,
            text="Paste from Clipboard",
            command=self._on_paste_clipboard,
        )
        paste_btn.pack(side=tk.LEFT, padx=5)

        # Read button
        read_btn = tk.Button(
            button_frame,
            text="Read",
            command=self._on_submit,
            bg="#4CAF50",
            fg="white",
            width=10,
        )
        read_btn.pack(side=tk.LEFT, padx=5)

        # Cancel button
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            width=10,
        )
        cancel_btn.pack(side=tk.LEFT, padx=5)

    def _on_paste_clipboard(self):
        """Paste clipboard content to text area."""
        try:
            clipboard_content = self._window.clipboard_get()
            self._text_area.delete("1.0", tk.END)
            self._text_area.insert("1.0", clipboard_content)
        except tk.TclError:
            # Clipboard is empty or unavailable
            pass

    def _on_submit(self):
        """Submit the entered text."""
        text = self._text_area.get("1.0", tk.END).strip()

        if not text:
            return

        # Call callback with text
        self._callback(text)

        # Close window
        self._window.destroy()

    def _on_cancel(self):
        """Cancel and close window."""
        self._window.destroy()

    def show(self):
        """Display the window."""
        logger.info("showing_input_window")
        self._window.deiconify()
        self._window.focus_force()
        logger.debug("input_window_visible")
