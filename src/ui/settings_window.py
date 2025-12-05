"""Settings window for configuration."""

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, ttk

from src.logger import get_logger
from src.settings import Settings

logger = get_logger(__name__)


class SettingsWindow:
    """Dialog for application settings."""

    def __init__(self, settings: Settings, available_voices: list[str]):
        """Initialize SettingsWindow.

        Args:
            settings: Settings instance
            available_voices: List of available voice names
        """
        logger.info("creating_settings_window", voice_count=len(available_voices))
        self._settings = settings
        self._available_voices = available_voices

        # Create window
        self._window = tk.Toplevel()
        self._window.title("Settings")

        # Remove window decorations for cleaner look (must be before geometry)
        self._window.overrideredirect(True)

        # Position window in top-right corner (same as input window)
        window_width = 480
        window_height = 320

        # Update to get screen dimensions
        self._window.update_idletasks()
        screen_width = self._window.winfo_screenwidth()

        # Position very close to top-right (10px from right edge, 40px from top for menu bar)
        x_position = screen_width - window_width - 10
        y_position = 40

        self._window.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")
        self._window.resizable(False, False)
        self._window.lift()
        self._window.attributes('-topmost', True)
        self._window.after_idle(self._window.attributes, '-topmost', False)

        # Variables for form fields
        self._voice_var = tk.StringVar()
        self._speed_var = tk.DoubleVar()
        self._output_dir_var = tk.StringVar()

        # Load current settings
        self._load_settings()

        # Create UI
        self._create_widgets()
        logger.debug("settings_window_created")

    def _load_settings(self):
        """Load current settings into variables."""
        self._voice_var.set(self._settings.get("voice"))
        self._speed_var.set(self._settings.get("speed"))
        self._output_dir_var.set(self._settings.get("output_directory"))

    def _create_widgets(self):
        """Create all window widgets."""
        # Container with border
        container = tk.Frame(
            self._window,
            bg="white",
            highlightbackground="#d1d1d6",
            highlightthickness=1,
        )
        container.pack(fill=tk.BOTH, expand=True, padx=0, pady=0)

        # Main frame with padding
        main_frame = tk.Frame(container, padx=20, pady=20, bg="white")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Voice selection
        voice_label = tk.Label(
            main_frame,
            text="Voice:",
            font=("SF Pro Text", 11),
            fg="#86868b",
            bg="white",
            anchor="w",
        )
        voice_label.grid(row=0, column=0, sticky="w", pady=(0, 6))

        voice_combo = ttk.Combobox(
            main_frame,
            textvariable=self._voice_var,
            values=self._available_voices,
            state="readonly",
            font=("SF Pro Text", 12),
            width=35,
        )
        voice_combo.grid(row=0, column=1, columnspan=2, sticky="ew", pady=(0, 15))

        # Speed control
        speed_label = tk.Label(
            main_frame,
            text="Speed:",
            font=("SF Pro Text", 11),
            fg="#86868b",
            bg="white",
            anchor="w",
        )
        speed_label.grid(row=1, column=0, sticky="w", pady=(0, 6))

        # Speed frame with slider and value label
        speed_frame = tk.Frame(main_frame, bg="white")
        speed_frame.grid(row=1, column=1, columnspan=2, sticky="ew", pady=(0, 15))

        speed_scale = tk.Scale(
            speed_frame,
            variable=self._speed_var,
            from_=0.5,
            to=2.0,
            resolution=0.25,
            orient=tk.HORIZONTAL,
            font=("SF Pro Text", 11),
            bg="white",
            fg="#1d1d1f",
            highlightthickness=0,
            troughcolor="#f5f5f7",
            showvalue=False,
        )
        speed_scale.pack(side=tk.LEFT, fill=tk.X, expand=True)

        # Value label
        self._speed_value_label = tk.Label(
            speed_frame,
            text=f"{self._speed_var.get()}x",
            font=("SF Pro Text", 11),
            fg="#1d1d1f",
            bg="white",
            width=5,
        )
        self._speed_value_label.pack(side=tk.RIGHT, padx=(8, 0))

        # Update label when slider changes
        speed_scale.config(command=self._on_speed_change)

        # Output directory
        output_label = tk.Label(
            main_frame,
            text="Output Directory:",
            font=("SF Pro Text", 11),
            fg="#86868b",
            bg="white",
            anchor="w",
        )
        output_label.grid(row=2, column=0, sticky="w", pady=(0, 6))

        output_entry = tk.Entry(
            main_frame,
            textvariable=self._output_dir_var,
            font=("SF Pro Text", 12),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            bg="#f5f5f7",
        )
        output_entry.grid(row=2, column=1, sticky="ew", pady=(0, 15), ipady=6)

        browse_btn = tk.Button(
            main_frame,
            text="Browse",
            command=self._browse_directory,
            font=("SF Pro Text", 11),
            relief=tk.FLAT,
            bd=0,
            bg="#f5f5f7",
            fg="#007AFF",
            padx=12,
            pady=6,
        )
        browse_btn.grid(row=2, column=2, padx=(8, 0), pady=(0, 15))

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Button frame
        button_frame = tk.Frame(main_frame, bg="white")
        button_frame.grid(row=3, column=0, columnspan=3, pady=(20, 0), sticky="e")

        # Cancel button (secondary)
        cancel_btn = tk.Button(
            button_frame,
            text="Cancel",
            command=self._on_cancel,
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            bg="white",
            fg="#86868b",
            padx=25,
            pady=8,
        )
        cancel_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Save button (primary, Mac-style)
        save_btn = tk.Button(
            button_frame,
            text="Save",
            command=self._on_save,
            bg="#007AFF",
            fg="white",
            font=("SF Pro Text", 13),
            relief=tk.FLAT,
            bd=0,
            highlightthickness=0,
            padx=35,
            pady=8,
            activebackground="#0051D5",
            activeforeground="white",
        )
        save_btn.pack(side=tk.LEFT)

    def _on_speed_change(self, value):
        """Update speed value label.

        Args:
            value: New speed value from slider
        """
        self._speed_value_label.config(text=f"{float(value)}x")

    def _browse_directory(self):
        """Open directory browser."""
        directory = filedialog.askdirectory(
            initialdir=Path(self._output_dir_var.get()).expanduser(),
            title="Select Output Directory",
        )
        if directory:
            self._output_dir_var.set(directory)

    def _on_save(self):
        """Save settings and close."""
        # Update settings
        self._settings.set("voice", self._voice_var.get())
        self._settings.set("speed", self._speed_var.get())
        self._settings.set("output_directory", self._output_dir_var.get())

        # Save to file
        self._settings.save()

        # Close window
        self._window.destroy()

    def _on_cancel(self):
        """Cancel and close without saving."""
        self._window.destroy()

    def show(self):
        """Display the window."""
        logger.info("showing_settings_window")
        self._window.deiconify()
        self._window.focus_force()
        logger.debug("settings_window_visible")
