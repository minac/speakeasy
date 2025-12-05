"""Input window for entering text or URLs."""

import tkinter as tk
from collections.abc import Callable

from src.logger import get_logger

logger = get_logger(__name__)


class InputWindow:
    """Dialog for text or URL input."""

    def __init__(
        self,
        callback: Callable[[str], None],
        stop_callback: Callable[[], None] | None = None,
    ):
        """Initialize InputWindow.

        Args:
            callback: Function to call with submitted text (for Read/Play)
            stop_callback: Function to call when stop is clicked
        """
        logger.info("creating_input_window")
        self._callback = callback
        self._stop_callback = stop_callback
        self._is_playing = False
        self._window = tk.Toplevel()
        self._window.title("Piper TTS Reader")

        # Position window in top-right corner
        window_width = 400
        window_height = 200

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
        main_frame = tk.Frame(self._window, padx=20, pady=20, bg="#f5f5f7")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions label (Mac-style)
        instructions = tk.Label(
            main_frame,
            text="Enter text or paste a URL to read aloud:",
            font=("SF Pro Text", 12),
            fg="#1d1d1f",
            bg="#f5f5f7",
            anchor="w",
        )
        instructions.pack(pady=(0, 10), fill=tk.X)

        # Text area frame for border effect
        text_frame = tk.Frame(main_frame, bg="#e5e5ea", bd=1, relief=tk.SOLID)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Text area (Mac-style with placeholder effect)
        self._text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=5,
            highlightthickness=0,
            bg="white",
            fg="#1d1d1f",
            insertbackground="#007AFF",  # Blue cursor
            height=4,
        )
        self._text_area.pack(fill=tk.BOTH, expand=True)
        # Focus the text area so cursor blinks
        self._text_area.focus_set()

        # Play button (Mac-style accent button with proper visibility)
        self._play_btn = tk.Button(
            main_frame,
            text="Play",
            command=self._on_play,
            bg="#007AFF",
            fg="white",
            font=("SF Pro Text", 14, "bold"),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=30,
            pady=10,
            activebackground="#0051D5",
            activeforeground="white",
        )
        self._play_btn.pack()

        # Stop button (initially hidden)
        self._stop_btn = tk.Button(
            main_frame,
            text="Stop",
            command=self._on_stop,
            bg="#FF3B30",  # macOS red
            fg="white",
            font=("SF Pro Text", 14, "bold"),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=30,
            pady=10,
            activebackground="#D32F2F",
            activeforeground="white",
        )
        # Don't pack initially - will show based on state

    def _on_paste_clipboard(self):
        """Paste clipboard content to text area."""
        try:
            clipboard_content = self._window.clipboard_get()
            self._text_area.delete("1.0", tk.END)
            self._text_area.insert("1.0", clipboard_content)
        except tk.TclError:
            # Clipboard is empty or unavailable
            pass

    def _on_play(self):
        """Play button clicked - start reading."""
        text = self._text_area.get("1.0", tk.END).strip()

        if not text:
            return

        # Update button visibility
        self._is_playing = True
        self._play_btn.pack_forget()
        self._stop_btn.pack()

        # Call callback with text
        self._callback(text)

    def _on_stop(self):
        """Stop button clicked - stop playback."""
        # Update button visibility
        self._is_playing = False
        self._stop_btn.pack_forget()
        self._play_btn.pack()

        # Call stop callback if provided
        if self._stop_callback:
            self._stop_callback()

    def set_playing(self, is_playing: bool):
        """Update playback state externally.

        Args:
            is_playing: True if playing, False if stopped
        """
        self._is_playing = is_playing
        if is_playing:
            self._play_btn.pack_forget()
            self._stop_btn.pack()
        else:
            self._stop_btn.pack_forget()
            self._play_btn.pack()

    def show(self):
        """Display the window."""
        logger.info("showing_input_window")
        self._window.deiconify()
        self._window.focus_force()
        logger.debug("input_window_visible")
