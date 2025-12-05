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
        download_callback: Callable[[], None] | None = None,
    ):
        """Initialize InputWindow.

        Args:
            callback: Function to call with submitted text (for Read/Play)
            stop_callback: Function to call when stop is clicked
            download_callback: Function to call when download is clicked
        """
        logger.info("creating_input_window")
        self._callback = callback
        self._stop_callback = stop_callback
        self._download_callback = download_callback
        self._is_playing = False
        self._has_audio = False
        self._window = tk.Toplevel()
        self._window.title("Piper TTS Reader")

        # Remove window decorations for cleaner look (must be before geometry)
        self._window.overrideredirect(True)

        # Position window in top-right corner
        window_width = 420
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
        # Container with rounded corners and shadow effect
        container = tk.Frame(
            self._window,
            bg="white",
            highlightbackground="#d1d1d6",
            highlightthickness=1,
        )
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Main frame with padding
        main_frame = tk.Frame(container, padx=18, pady=18, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Instructions label (Mac-style, lighter weight)
        instructions = tk.Label(
            main_frame,
            text="Enter text or URL:",
            font=("SF Pro Text", 11),
            fg="#86868b",
            bg="white",
            anchor="w",
        )
        instructions.pack(pady=(0, 8), fill=tk.X)

        # Text area frame for subtle border
        text_frame = tk.Frame(main_frame, bg="#f5f5f7", bd=0)
        text_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        # Text area (Mac-style minimal)
        self._text_area = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=8,
            highlightthickness=0,
            bg="#f5f5f7",
            fg="#1d1d1f",
            insertbackground="#007AFF",  # Blue cursor
            height=5,
        )
        self._text_area.pack(fill=tk.BOTH, expand=True)
        # Bind text change events to update button state
        self._text_area.bind("<<Modified>>", self._on_text_change)
        # Focus the text area so cursor blinks
        self._text_area.focus_set()

        # Button container
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.pack(fill=tk.X)

        # Download button (left side, initially disabled)
        self._download_btn = tk.Button(
            button_frame,
            text="Download MP3",
            command=self._on_download,
            bg="#34C759",  # macOS green
            fg="white",
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=20,
            pady=8,
            activebackground="#30A14E",
            activeforeground="white",
            state=tk.DISABLED,  # Initially disabled
        )
        self._download_btn.pack(side=tk.LEFT)

        # Play button (Mac-style rounded)
        self._play_btn = tk.Button(
            button_frame,
            text="Play",
            command=self._on_play,
            bg="#007AFF",
            fg="white",
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=40,
            pady=8,
            activebackground="#0051D5",
            activeforeground="white",
            state=tk.DISABLED,  # Initially disabled
        )
        self._play_btn.pack(side=tk.RIGHT)

        # Stop button (initially hidden)
        self._stop_btn = tk.Button(
            button_frame,
            text="Stop",
            command=self._on_stop,
            bg="#FF3B30",  # macOS red
            fg="white",
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=40,
            pady=8,
            activebackground="#D32F2F",
            activeforeground="white",
        )
        # Don't pack initially - will show based on state

    def _on_text_change(self, event=None):
        """Handle text area changes to enable/disable Play button."""
        # Reset the modified flag
        if self._text_area.edit_modified():
            self._text_area.edit_modified(False)

            # Only update button state if not playing
            if not self._is_playing:
                text = self._text_area.get("1.0", tk.END).strip()
                if text:
                    self._play_btn.config(state=tk.NORMAL)
                else:
                    self._play_btn.config(state=tk.DISABLED)

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
        self._stop_btn.pack(side=tk.RIGHT)

        # Call callback with text
        self._callback(text)

    def _on_stop(self):
        """Stop button clicked - stop playback."""
        # Update button visibility
        self._is_playing = False
        self._stop_btn.pack_forget()
        self._play_btn.pack(side=tk.RIGHT)

        # Re-enable play button if there's text
        text = self._text_area.get("1.0", tk.END).strip()
        if text:
            self._play_btn.config(state=tk.NORMAL)

        # Call stop callback if provided
        if self._stop_callback:
            self._stop_callback()

    def _on_download(self):
        """Download button clicked - export to MP3."""
        if self._download_callback:
            self._download_callback()

    def set_playing(self, is_playing: bool):
        """Update playback state externally.

        Args:
            is_playing: True if playing, False if stopped
        """
        self._is_playing = is_playing
        if is_playing:
            self._play_btn.pack_forget()
            self._stop_btn.pack(side=tk.RIGHT)
        else:
            self._stop_btn.pack_forget()
            self._play_btn.pack(side=tk.RIGHT)

    def set_audio_available(self, available: bool):
        """Enable/disable download button based on audio availability.

        Args:
            available: True if audio is ready for download
        """
        self._has_audio = available
        if available:
            self._download_btn.config(state=tk.NORMAL)
        else:
            self._download_btn.config(state=tk.DISABLED)

    def show(self):
        """Display the window."""
        logger.info("showing_input_window")
        self._window.deiconify()
        self._window.focus_force()
        logger.debug("input_window_visible")
