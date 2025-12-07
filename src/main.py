"""Main application entry point.

Architecture Notes (macOS Threading):
-------------------------------------
On macOS, there are conflicting main-thread requirements:
- pystray (NSApplication) wants the main thread
- tkinter also requires the main thread for GUI operations
- pynput uses Core Foundation run loops with main thread affinity

Solution: Use queue-based coordination
- tkinter owns the main thread and runs mainloop()
- pystray runs detached via run_detached()
- pystray callbacks post requests to a thread-safe queue
- tkinter polls the queue via after() and handles window creation

This keeps all tkinter operations on the main thread while allowing
pystray to function in a separate context.
"""

import queue
import sys
import tkinter as tk
from pathlib import Path

from src.audio_player import AudioPlayer
from src.hotkeys import HotkeyManager
from src.logger import configure_logging, get_logger
from src.settings import Settings
from src.text_extractor import TextExtractor
from src.tray import TrayApplication
from src.tts_engine import PiperTTSEngine
from src.ui.input_window import InputWindow
from src.ui.settings_window import SettingsWindow

logger = get_logger(__name__)

# Queue message types
MSG_SHOW_INPUT_WINDOW = "show_input_window"
MSG_SHOW_SETTINGS_WINDOW = "show_settings_window"
MSG_QUIT = "quit"


class PiperTTSApp:
    """Main application coordinator."""

    def __init__(self):
        """Initialize application."""
        logger.info("initializing_piper_tts_app")

        # Thread-safe queue for cross-thread communication
        # pystray callbacks post to this, tkinter mainloop polls it
        self._ui_queue = queue.Queue()

        # Initialize hidden tkinter root for Toplevel windows
        # This MUST be created on the main thread
        self._tk_root = tk.Tk()
        self._tk_root.withdraw()
        logger.debug("tkinter_root_created")

        # Load settings
        self._settings = Settings()
        logger.debug("settings_loaded")

        # Initialize TTS engine
        voices_dir = Path(__file__).parent.parent / "voices"
        self._tts_engine = PiperTTSEngine(str(voices_dir))

        # Load voice from settings (or first available voice)
        voice_name = self._settings.get("voice")
        available_voices = self._tts_engine.discover_voices()
        if voice_name and voice_name in available_voices:
            self._tts_engine.load_voice(voice_name)
            logger.debug("voice_loaded_from_settings", voice=voice_name)
        elif available_voices:
            # Load first available voice if configured voice not found
            self._tts_engine.load_voice(available_voices[0])
            logger.info("voice_loaded_fallback", voice=available_voices[0])
        else:
            logger.warning("no_voices_available")

        # Initialize audio player
        self._audio_player = AudioPlayer()

        # Initialize text extractor
        self._text_extractor = TextExtractor()

        # Initialize hotkey manager (disabled on macOS due to threading conflicts)
        self._hotkey_manager = HotkeyManager()

        # Initialize tray application
        self._tray_app = TrayApplication()

        # Wire up event handlers
        self._setup_event_handlers()

        logger.info("piper_tts_app_initialized")

    def _setup_event_handlers(self):
        """Wire up all event handlers."""
        # Register hotkeys (disabled on macOS - see run() method)
        shortcuts = self._settings.get("shortcuts")
        if isinstance(shortcuts, dict):
            if "play_pause" in shortcuts:
                self._hotkey_manager.register(
                    shortcuts["play_pause"], self._on_play_pause
                )
            if "stop" in shortcuts:
                self._hotkey_manager.register(shortcuts["stop"], self._on_stop)

        # Connect tray menu actions
        # IMPORTANT: These callbacks run in pystray's thread, NOT the main thread.
        # They must NOT directly create tkinter windows. Instead, they post
        # requests to the queue which the main thread processes.
        self._tray_app._read_text = lambda icon, item: self._queue_show_input_window()
        self._tray_app._open_settings = lambda icon, item: self._queue_show_settings_window()
        self._tray_app._quit = lambda icon, item: self._queue_quit()

        # Audio player completion callback
        self._audio_player.set_completion_callback(self._on_playback_complete)

    def _queue_show_input_window(self):
        """Queue a request to show the input window (thread-safe)."""
        logger.debug("queueing_input_window_request")
        self._ui_queue.put(MSG_SHOW_INPUT_WINDOW)

    def _queue_show_settings_window(self):
        """Queue a request to show the settings window (thread-safe)."""
        logger.debug("queueing_settings_window_request")
        self._ui_queue.put(MSG_SHOW_SETTINGS_WINDOW)

    def _queue_quit(self):
        """Queue a quit request (thread-safe)."""
        logger.debug("queueing_quit_request")
        self._ui_queue.put(MSG_QUIT)

    def _process_ui_queue(self):
        """Process pending UI requests from the queue.

        This runs on the main thread via tkinter's after() mechanism.
        """
        try:
            while True:
                try:
                    msg = self._ui_queue.get_nowait()
                    logger.debug("processing_queue_message", message=msg)

                    if msg == MSG_SHOW_INPUT_WINDOW:
                        self._show_input_window()
                    elif msg == MSG_SHOW_SETTINGS_WINDOW:
                        self._on_open_settings()
                    elif msg == MSG_QUIT:
                        self._shutdown()
                        return  # Don't schedule another check

                except queue.Empty:
                    break
        except Exception as e:
            logger.error("queue_processing_error", error=str(e), exc_info=True)

        # Schedule next queue check (50ms interval)
        self._tk_root.after(50, self._process_ui_queue)

    def _on_play_pause(self):
        """Handle play/pause action."""
        state = self._audio_player.get_state()
        logger.info("play_pause_clicked", state=state)

        if state == "STOPPED":
            # Queue showing input window (don't call directly from pystray thread)
            self._queue_show_input_window()
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
        logger.info("stop_clicked")
        self._audio_player.stop()

    def _on_open_settings(self):
        """Open settings window.

        This MUST be called from the main thread (via queue processing).
        """
        logger.info("showing_settings_window")
        available_voices = self._tts_engine.discover_voices()
        settings_window = SettingsWindow(self._settings, available_voices)
        settings_window.show()

        # Reload voice if changed
        new_voice = self._settings.get("voice")
        if new_voice and new_voice != self._tts_engine.current_voice:
            self._tts_engine.load_voice(new_voice)

    def _on_playback_complete(self):
        """Handle playback completion."""
        logger.debug("playback_complete")

    def _show_input_window(self):
        """Show input window for text/URL entry.

        This MUST be called from the main thread (via queue processing).
        """
        logger.info("showing_input_window")
        input_window = InputWindow(
            callback=self._on_text_submitted,
            stop_callback=self._on_stop
        )
        input_window.show()

    def _on_text_submitted(self, text: str):
        """Handle text submission from input window."""
        logger.info("text_submitted", length=len(text))

        # Extract text (handles URLs)
        logger.debug("extracting_text", is_url=text.startswith("http"))
        extracted_text = self._text_extractor.extract(text)
        logger.info("text_extracted", extracted_length=len(extracted_text))

        # Synthesize with current speed
        speed = self._settings.get("speed")
        logger.info("starting_synthesis", text_length=len(extracted_text), speed=speed)
        audio_data, sample_rate = self._tts_engine.synthesize(extracted_text, speed)
        logger.info("synthesis_complete", audio_samples=len(audio_data), sample_rate=sample_rate)

        # Play
        logger.info("starting_playback")
        self._audio_player.play(audio_data)
        logger.info("playback_started")

    def _shutdown(self):
        """Shutdown the application gracefully."""
        logger.info("shutting_down")

        # Stop audio playback
        self._audio_player.stop()

        # Stop hotkey listener if running
        self._hotkey_manager.stop()

        # Stop pystray icon
        self._tray_app.stop()

        # Quit tkinter mainloop
        self._tk_root.quit()

    def run(self):
        """Start the application."""
        logger.info("starting_application")

        # NOTE: Global hotkeys are disabled on macOS due to threading conflicts.
        # pynput's GlobalHotKeys uses Core Foundation run loops which conflict
        # with both pystray (NSApplication) and tkinter when running together.
        # This causes GIL errors: "PyEval_RestoreThread: the function must be
        # called with the GIL held, but the GIL is released"
        #
        # To re-enable hotkeys, either:
        # 1. Use a macOS-native hotkey solution (e.g., PyObjC + Carbon)
        # 2. Run pynput in a completely isolated process
        # 3. Use tkinter's bind() for window-specific shortcuts instead
        if sys.platform != "darwin":
            self._hotkey_manager.start()
            logger.debug("hotkey_manager_started")
        else:
            logger.warning("hotkeys_disabled_macos",
                         reason="pynput conflicts with pystray/tkinter on macOS")

        # Start queue processing on the main thread
        self._tk_root.after(50, self._process_ui_queue)
        logger.debug("queue_processing_started")

        # Run pystray detached - this allows it to work alongside tkinter
        # On macOS, run_detached() is required when integrating with other mainloops
        logger.info("starting_tray_detached")
        self._tray_app.run_detached()

        # Run tkinter mainloop on the main thread (REQUIRED on macOS)
        # This is the primary event loop - all GUI operations happen here
        logger.info("starting_tkinter_mainloop")
        self._tk_root.mainloop()

        logger.info("application_stopped")


def main():
    """Entry point."""
    configure_logging("INFO")
    logger.info("piper_tts_starting")

    app = PiperTTSApp()
    app.run()


if __name__ == "__main__":
    main()
