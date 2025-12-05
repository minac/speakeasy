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

        # Position window in top-right corner
        window_width = 400
        window_height = 280

        # Update to get screen dimensions
        self._window.update_idletasks()
        screen_width = self._window.winfo_screenwidth()

        # Position very close to top-right (10px from right edge, 40px from top for menu bar)
        x_position = screen_width - window_width - 10
        y_position = 40

        self._window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self._window.lift()
        self._window.attributes('-topmost', True)
        self._window.after_idle(self._window.attributes, '-topmost', False)

        # Bind ESC key to close window
        self._window.bind('<Escape>', lambda e: self._window.destroy())

        # Bind Cmd+V to paste (macOS)
        self._window.bind('<Command-v>', lambda e: self._on_paste_clipboard())

        # Create UI elements
        self._create_widgets()
        logger.debug("input_window_created")

    def _create_widgets(self):
        """Create all window widgets."""
        # Main frame with padding
        main_frame = tk.Frame(self._window, padx=15, pady=15, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions label (Mac-style)
        instructions = tk.Label(
            main_frame,
            text="Enter text or paste a URL to read aloud:",
            font=("SF Pro Text", 11),
            fg="#333333",
            bg="white",
            anchor="w",
        )
        instructions.pack(pady=(0, 8), fill=tk.X)

        # Text area frame for border effect
        text_frame = tk.Frame(main_frame, bg="#d1d1d6", bd=0)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        # Text area (smaller, Mac-style)
        self._text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("SF Pro Text", 12),
            relief=tk.FLAT,
            bd=3,
            highlightthickness=0,
            height=8,
        )
        self._text_area.pack(fill=tk.BOTH, expand=True)

        # Read button (Mac-style accent button)
        read_btn = tk.Button(
            main_frame,
            text="Read",
            command=self._on_submit,
            bg="#007AFF",
            fg="white",
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=20,
            pady=8,
        )
        read_btn.pack()

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

    def show(self):
        """Display the window."""
        logger.info("showing_input_window")
        self._window.deiconify()
        self._window.focus_force()
        logger.debug("input_window_visible")
