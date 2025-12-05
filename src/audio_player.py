"""Audio playback controller with speed control and state management"""

import logging
import threading
from collections.abc import Callable
from enum import Enum

import numpy as np
import sounddevice as sd

logger = logging.getLogger(__name__)


class PlaybackState(Enum):
    """Playback state enumeration"""

    STOPPED = "stopped"
    PLAYING = "playing"
    PAUSED = "paused"


class AudioPlayer:
    """Audio player with playback controls and speed adjustment"""

    def __init__(self, sample_rate: int = 22050):
        """
        Initialize audio player

        Args:
            sample_rate: Audio sample rate in Hz
        """
        self.sample_rate = sample_rate
        self._state = PlaybackState.STOPPED
        self._audio_data: np.ndarray | None = None
        self._position = 0  # Current position in samples
        self._speed = 1.0
        self._stream: sd.OutputStream | None = None
        self._completion_callback: Callable[[], None] | None = None
        self._lock = threading.Lock()

        logger.info(f"Initialized audio player with sample rate: {sample_rate}")

    @property
    def state(self) -> PlaybackState:
        """Get current playback state"""
        return self._state

    @property
    def position(self) -> int:
        """Get current playback position in samples"""
        return self._position

    @property
    def duration(self) -> float:
        """Get total audio duration in seconds"""
        if self._audio_data is None:
            return 0.0
        return len(self._audio_data) / self.sample_rate

    @property
    def speed(self) -> float:
        """Get current playback speed"""
        return self._speed

    def play(self, audio_data: np.ndarray) -> None:
        """
        Start playing audio

        Args:
            audio_data: Audio samples as numpy array
        """
        logger.debug("play_called", audio_samples=len(audio_data))

        # Stop any existing playback OUTSIDE the lock to avoid deadlock
        # The stream callbacks may try to acquire the lock
        old_stream = None
        with self._lock:
            if self._stream is not None:
                logger.debug("storing_stream_reference_for_cleanup")
                old_stream = self._stream
                self._stream = None

        # Close the old stream outside the lock
        if old_stream is not None:
            logger.debug("stopping_existing_stream")
            try:
                old_stream.stop()
                old_stream.close()
            except Exception as e:
                logger.warning("error_closing_stream", error=str(e))

        # Now start new playback with the lock
        with self._lock:
            self._audio_data = audio_data
            self._position = 0
            logger.debug("starting_playback_stream")
            self._start_playback()
            logger.debug("playback_stream_started")

        logger.info(f"Started playback of {len(audio_data)} samples")

    def pause(self) -> None:
        """Pause playback without losing position"""
        with self._lock:
            if self._state != PlaybackState.PLAYING:
                return

            if self._stream is not None:
                self._stream.stop()

            self._state = PlaybackState.PAUSED
            logger.info(f"Paused playback at position {self._position}")

    def resume(self) -> None:
        """Resume playback from pause position"""
        with self._lock:
            if self._state != PlaybackState.PAUSED:
                return

            if self._audio_data is None:
                return

            self._start_playback()
            logger.info(f"Resumed playback from position {self._position}")

    def stop(self) -> None:
        """Stop playback and reset position"""
        with self._lock:
            if self._stream is not None:
                self._stream.stop()
                self._stream.close()
                self._stream = None

            self._state = PlaybackState.STOPPED
            self._position = 0
            logger.info("Stopped playback")

    def set_speed(self, speed: float) -> None:
        """
        Set playback speed

        Args:
            speed: Speed multiplier (0.5 = half speed, 2.0 = double speed)
        """
        if speed <= 0:
            raise ValueError("Speed must be positive")

        with self._lock:
            old_speed = self._speed
            self._speed = speed

            # If playing, we need to adjust the stream
            # For simplicity, we'll keep playing at the same position
            # A more sophisticated implementation would recreate the stream

            logger.info(f"Speed changed from {old_speed}x to {speed}x")

    def set_completion_callback(self, callback: Callable[[], None]) -> None:
        """
        Set callback to be called when playback completes

        Args:
            callback: Function to call on completion
        """
        self._completion_callback = callback

    def _start_playback(self) -> None:
        """Internal method to start/resume playback"""
        if self._audio_data is None:
            return

        # Apply speed adjustment to audio
        adjusted_audio = self._apply_speed(self._audio_data[self._position :])

        # Create output stream
        self._stream = sd.OutputStream(
            samplerate=self.sample_rate,
            channels=1,
            dtype="int16",
            callback=self._audio_callback,
            finished_callback=self._on_stream_finished,
        )

        self._adjusted_audio = adjusted_audio
        self._adjusted_position = 0

        self._stream.start()
        self._state = PlaybackState.PLAYING

    def _apply_speed(self, audio_data: np.ndarray) -> np.ndarray:
        """
        Apply speed adjustment to audio

        Args:
            audio_data: Original audio samples

        Returns:
            Speed-adjusted audio samples
        """
        if self._speed == 1.0:
            return audio_data

        # Simple resampling for speed adjustment
        original_length = len(audio_data)
        new_length = int(original_length / self._speed)

        # Linear interpolation
        indices = np.linspace(0, original_length - 1, new_length)
        adjusted_audio = np.interp(indices, np.arange(original_length), audio_data)

        return adjusted_audio.astype(np.int16)

    def _audio_callback(
        self, outdata: np.ndarray, frames: int, time_info, status
    ) -> None:
        """
        Callback for audio stream

        Args:
            outdata: Output buffer to fill
            frames: Number of frames requested
            time_info: Time information
            status: Stream status
        """
        if status:
            logger.warning(f"Audio stream status: {status}")

        # Get next chunk of audio
        remaining = len(self._adjusted_audio) - self._adjusted_position
        chunk_size = min(frames, remaining)

        if chunk_size > 0:
            chunk = self._adjusted_audio[
                self._adjusted_position : self._adjusted_position + chunk_size
            ]
            outdata[:chunk_size, 0] = chunk
            self._adjusted_position += chunk_size

            # Update original position (approximate)
            self._position += int(chunk_size * self._speed)

        # Fill remaining with silence if needed
        if chunk_size < frames:
            outdata[chunk_size:, 0] = 0

    def _on_stream_finished(self) -> None:
        """Callback when stream finishes"""
        with self._lock:
            self._state = PlaybackState.STOPPED
            self._position = 0

        logger.info("Playback completed")

        # Call completion callback if set
        if self._completion_callback is not None:
            self._completion_callback()

    def _on_completion(self) -> None:
        """Public method to trigger completion (for testing)"""
        self._on_stream_finished()
