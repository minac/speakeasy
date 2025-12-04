"""Main application entry point."""

import tkinter as tk
from pathlib import Path

from src.audio_player import AudioPlayer
from src.export import AudioExporter
from src.hotkeys import HotkeyManager
from src.logger import configure_logging, get_logger
from src.settings import Settings
from src.text_extractor import TextExtractor
from src.tray import TrayApplication
from src.tts_engine import PiperTTSEngine
from src.ui.input_window import InputWindow
from src.ui.settings_window import SettingsWindow

logger = get_logger(__name__)


class PiperTTSApp:
    """Main application coordinator."""

    def __init__(self):
        """Initialize application."""
        logger.info("initializing_piper_tts_app")

        # Tkinter root will be created lazily when first window is opened
        self._tk_root = None
        logger.debug("tkinter_deferred")

        # Load settings
        self._settings = Settings()
        logger.debug("settings_loaded")

        # Initialize TTS engine
        voices_dir = Path(__file__).parent.parent / "voices"
        self._tts_engine = PiperTTSEngine(str(voices_dir))

        # Load voice from settings
        voice_name = self._settings.get("voice")
        available_voices = self._tts_engine.discover_voices()
        if voice_name in available_voices:
            self._tts_engine.load_voice(voice_name)

        # Initialize audio player
        self._audio_player = AudioPlayer()

        # Initialize text extractor
        self._text_extractor = TextExtractor()

        # Initialize audio exporter
        output_dir = self._settings.get("output_directory")
        self._audio_exporter = AudioExporter(output_dir)

        # Initialize hotkey manager
        self._hotkey_manager = HotkeyManager()

        # Initialize tray application
        self._tray_app = TrayApplication()

        # Current state
        self._current_audio = None
        self._current_sample_rate = None
        self._current_text = None

        # Wire up event handlers
        self._setup_event_handlers()

        logger.info("piper_tts_app_initialized")

    def _setup_event_handlers(self):
        """Wire up all event handlers."""
        # Register hotkeys
        shortcuts = self._settings.get("shortcuts")
        if isinstance(shortcuts, dict):
            if "play_pause" in shortcuts:
                self._hotkey_manager.register(
                    shortcuts["play_pause"], self._on_play_pause
                )
            if "stop" in shortcuts:
                self._hotkey_manager.register(shortcuts["stop"], self._on_stop)

        # Connect tray menu actions
        def safe_read_text(icon, item):
            try:
                logger.info("read_text_handler_called")
                self._show_input_window()
            except Exception as e:
                logger.error("read_text_handler_failed", error=str(e), exc_info=True)

        def safe_settings(icon, item):
            try:
                logger.info("settings_handler_called")
                self._on_open_settings()
            except Exception as e:
                logger.error("settings_handler_failed", error=str(e), exc_info=True)

        self._tray_app._read_text = safe_read_text
        self._tray_app._play_pause = lambda icon, item: self._on_play_pause()
        self._tray_app._stop = lambda icon, item: self._on_stop()
        self._tray_app._download = lambda icon, item: self._on_download()
        self._tray_app._open_settings = safe_settings
        self._tray_app._change_speed = lambda icon, item, speed: self._on_speed_change(
            speed
        )

        # Audio player completion callback
        self._audio_player.set_completion_callback(self._on_playback_complete)

    def _on_play_pause(self):
        """Handle play/pause action."""
        state = self._audio_player.get_state()

        if state == "STOPPED":
            # Open input window
            self._show_input_window()
        elif state == "PLAYING":
            # Pause
            self._audio_player.pause()
            self._tray_app._is_playing = False
            self._tray_app._is_paused = True
        elif state == "PAUSED":
            # Resume
            self._audio_player.resume()
            self._tray_app._is_playing = True
            self._tray_app._is_paused = False

    def _on_stop(self):
        """Handle stop action."""
        self._audio_player.stop()
        self._tray_app._is_playing = False
        self._tray_app._is_paused = False

    def _on_download(self):
        """Handle download MP3 action."""
        if self._current_audio is not None and self._current_sample_rate is not None:
            output_path = self._audio_exporter.export(
                self._current_audio, self._current_sample_rate, self._current_text or ""
            )
            print(f"Saved to: {output_path}")

    def _on_speed_change(self, speed: float):
        """Handle speed change."""
        self._settings.set("speed", speed)
        self._settings.save()
        self._tray_app._speed = speed

        # If currently playing, restart with new speed
        if self._audio_player.get_state() == "PLAYING":
            self._audio_player.stop()
            if self._current_audio is not None:
                self._audio_player.play(
                    self._current_audio, self._current_sample_rate, speed
                )

    def _on_open_settings(self):
        """Open settings window."""
        logger.info("showing_settings_window")
        self._ensure_tk_root()
        available_voices = self._tts_engine.discover_voices()
        settings_window = SettingsWindow(self._settings, available_voices)
        settings_window.show()

        # Reload voice if changed
        new_voice = self._settings.get("voice")
        if new_voice != self._tts_engine.get_current_voice():
            self._tts_engine.load_voice(new_voice)

    def _on_playback_complete(self):
        """Handle playback completion."""
        self._tray_app._is_playing = False
        self._tray_app._is_paused = False

    def _show_input_window(self):
        """Show input window for text/URL entry."""
        logger.info("showing_input_window")
        self._ensure_tk_root()
        input_window = InputWindow(self._on_text_submitted)
        input_window.show()

    def _ensure_tk_root(self):
        """Ensure tkinter root exists."""
        if self._tk_root is None:
            logger.info("creating_tk_root")
            self._tk_root = tk.Tk()
            self._tk_root.withdraw()

    def _on_text_submitted(self, text: str):
        """Handle text submission from input window."""
        # Extract text (handles URLs)
        extracted_text = self._text_extractor.extract(text)
        self._current_text = extracted_text

        # Synthesize with current speed
        speed = self._settings.get("speed")
        audio_data, sample_rate = self._tts_engine.synthesize(extracted_text, speed)

        # Store for export
        self._current_audio = audio_data
        self._current_sample_rate = sample_rate
        self._tray_app._audio_data = audio_data
        self._tray_app._sample_rate = sample_rate

        # Play
        self._audio_player.play(audio_data, sample_rate, speed)
        self._tray_app._is_playing = True
        self._tray_app._is_paused = False

    def run(self):
        """Start the application."""
        logger.info("starting_application")

        # TODO: Hotkeys disabled temporarily due to GIL conflicts on macOS
        # with pystray + tkinter. Need to fix pynput threading.
        # self._hotkey_manager.start()
        # logger.debug("hotkey_manager_started")
        logger.warning("hotkeys_disabled_temporarily")

        # Run tray app (blocking)
        self._tray_app.run()

        logger.info("application_stopped")


def main():
    """Entry point."""
    configure_logging("INFO")
    logger.info("piper_tts_starting")

    app = PiperTTSApp()
    app.run()


if __name__ == "__main__":
    main()
