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
        window_width = 600
        window_height = 400

        # Update to get screen dimensions
        self._window.update_idletasks()
        screen_width = self._window.winfo_screenwidth()

        # Position near top-right (20px from right edge, 60px from top for menu bar)
        x_position = screen_width - window_width - 20
        y_position = 60

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

        # Read button (larger, more prominent)
        read_btn = tk.Button(
            button_frame,
            text="Read",
            command=self._on_submit,
            bg="#007AFF",  # macOS blue
            fg="white",
            font=("System", 14, "bold"),
            width=15,
            height=2,
            relief=tk.FLAT,
            cursor="hand2",
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
