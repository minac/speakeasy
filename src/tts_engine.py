"""Piper TTS Engine wrapper for text-to-speech synthesis"""
import logging
from pathlib import Path

import numpy as np
from piper import PiperVoice

logger = logging.getLogger(__name__)


class TTSError(Exception):
    """Base exception for TTS-related errors"""
    pass


class PiperTTSEngine:
    """Wrapper for Piper TTS synthesis with voice management and speed control"""

    def __init__(self, voices_dir: Path | str | None = None):
        """
        Initialize TTS engine

        Args:
            voices_dir: Directory containing voice model files (.onnx)
        """
        if voices_dir is None:
            self.voices_dir = Path(__file__).parent.parent / "voices"
        else:
            self.voices_dir = Path(voices_dir)
        self._voice: PiperVoice | None = None
        self._current_voice_name: str | None = None
        self._sample_rate: int = 22050

        logger.info(f"Initialized TTS engine with voices directory: {self.voices_dir}")

    def discover_voices(self) -> list[str]:
        """
        Scan voices directory for available voice models

        Returns:
            List of voice names (without .onnx extension)
        """
        if not self.voices_dir.exists():
            logger.warning(f"Voices directory does not exist: {self.voices_dir}")
            return []

        voice_files = self.voices_dir.glob("*.onnx")
        voices = [f.stem for f in voice_files]

        logger.info(f"Discovered {len(voices)} voices: {voices}")
        return voices

    def load_voice(self, voice_name: str) -> None:
        """
        Load a voice model for synthesis

        Args:
            voice_name: Name of the voice (without .onnx extension)

        Raises:
            FileNotFoundError: If voice file doesn't exist
        """
        voice_path = self.voices_dir / f"{voice_name}.onnx"

        if not voice_path.exists():
            raise FileNotFoundError(
                f"Voice file not found: {voice_path}. "
                f"Available voices: {self.discover_voices()}"
            )

        # Load voice model
        self._voice = PiperVoice.load(str(voice_path))
        self._current_voice_name = voice_name

        # Get sample rate from voice config if available
        config_path = voice_path.with_suffix(".onnx.json")
        if config_path.exists():
            import json
            with open(config_path) as f:
                config = json.load(f)
                self._sample_rate = config.get("sample_rate", 22050)

        logger.info(f"Loaded voice: {voice_name} (sample rate: {self._sample_rate})")

    @property
    def current_voice(self) -> str | None:
        """Get the currently loaded voice name"""
        return self._current_voice_name

    def synthesize(self, text: str, speed: float = 1.0) -> tuple[np.ndarray, int]:
        """
        Synthesize text to audio

        Args:
            text: Text to synthesize
            speed: Playback speed multiplier (0.5 = half speed, 2.0 = double speed)

        Returns:
            Tuple of (audio_data, sample_rate):
                - audio_data: numpy array of int16 samples
                - sample_rate: sample rate in Hz

        Raises:
            ValueError: If text is empty
            TTSError: If no voice is loaded or synthesis fails
        """
        # Validate input
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")

        if self._voice is None:
            raise TTSError(
                "No voice loaded. Call load_voice() first. "
                f"Available voices: {self.discover_voices()}"
            )

        try:
            # Synthesize audio chunks from text
            audio_chunks = list(self._voice.synthesize(text))

            # Concatenate all audio chunks into a single array
            audio_arrays = [chunk.audio_int16_array for chunk in audio_chunks]
            audio_data = np.concatenate(audio_arrays) if audio_arrays else np.array([], dtype=np.int16)

            # Apply speed adjustment if needed
            if speed != 1.0:
                audio_data = self._adjust_speed(audio_data, speed)

            logger.info(
                f"Synthesized {len(text)} characters to {len(audio_data)} samples "
                f"at {speed}x speed"
            )

            return audio_data, self._sample_rate

        except Exception as e:
            raise TTSError(f"Synthesis failed: {e}") from e

    def _adjust_speed(self, audio_data: np.ndarray, speed: float) -> np.ndarray:
        """
        Adjust audio playback speed

        Args:
            audio_data: Original audio samples
            speed: Speed multiplier

        Returns:
            Speed-adjusted audio samples
        """
        # Simple resampling approach
        # For better quality, could use scipy.signal.resample or librosa
        original_length = len(audio_data)
        new_length = int(original_length / speed)

        # Linear interpolation for speed adjustment
        indices = np.linspace(0, original_length - 1, new_length)
        adjusted_audio = np.interp(indices, np.arange(original_length), audio_data)

        return adjusted_audio.astype(np.int16)
