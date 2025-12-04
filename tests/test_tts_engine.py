"""Tests for TTS Engine"""

import pytest

from src.tts_engine import PiperTTSEngine, TTSError


class TestPiperTTSEngine:
    def test_discover_voices_returns_list(self, temp_voices_dir, mock_voice_file):
        """Should return list of available voice models"""
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)
        voices = engine.discover_voices()

        assert isinstance(voices, list)
        assert len(voices) > 0
        assert "en_US-test-medium" in voices

    def test_discover_voices_empty_directory(self, temp_voices_dir):
        """Should return empty list when no voices installed"""
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)
        voices = engine.discover_voices()

        assert isinstance(voices, list)
        assert len(voices) == 0

    def test_synthesize_returns_audio_data(self, temp_voices_dir, mock_voice_file, mocker):
        """Should return numpy array of audio samples"""
        import io
        import wave

        import numpy as np

        # Create mock WAV data
        mock_wav = io.BytesIO()
        with wave.open(mock_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(22050)
            # Write 1024 samples of silence
            wf.writeframes(b"\x00" * 2048)
        mock_wav.seek(0)

        # Mock piper-tts synthesis
        def mock_synthesize(text, output_stream):
            output_stream.write(mock_wav.getvalue())

        mocker.patch("piper.PiperVoice.load")
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)
        engine.load_voice("en_US-test-medium")

        # Mock the synthesize method
        mocker.patch.object(engine._voice, "synthesize", side_effect=mock_synthesize)

        audio_data = engine.synthesize("Hello world")

        assert audio_data is not None
        assert len(audio_data) > 0
        assert isinstance(audio_data, np.ndarray)

    def test_synthesize_with_speed_adjustment(self, temp_voices_dir, mock_voice_file, mocker):
        """Should adjust audio speed correctly"""
        import io
        import wave

        # Create mock WAV data with more samples
        mock_wav = io.BytesIO()
        with wave.open(mock_wav, "wb") as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)  # 16-bit
            wf.setframerate(22050)
            # Write 44100 samples (2 seconds at 22050 Hz)
            wf.writeframes(b"\x00" * 88200)
        mock_wav.seek(0)

        # Mock piper-tts synthesis
        def mock_synthesize(text, output_stream):
            output_stream.write(mock_wav.getvalue())

        mocker.patch("piper.PiperVoice.load")
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)
        engine.load_voice("en_US-test-medium")

        # Mock the synthesize method
        mocker.patch.object(engine._voice, "synthesize", side_effect=mock_synthesize)

        # Test different speeds
        audio_normal = engine.synthesize("Hello", speed=1.0)
        audio_fast = engine.synthesize("Hello", speed=2.0)

        # Faster speed should produce shorter audio
        assert len(audio_fast) < len(audio_normal)

    def test_synthesize_empty_text_raises(self, temp_voices_dir, mock_voice_file, mocker):
        """Should raise ValueError for empty text"""
        mocker.patch("piper.PiperVoice.load")
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)
        engine.load_voice("en_US-test-medium")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            engine.synthesize("")

        with pytest.raises(ValueError, match="Text cannot be empty"):
            engine.synthesize("   ")

    def test_synthesize_missing_voice_raises(self, temp_voices_dir):
        """Should raise TTSError when no voice is loaded"""
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)

        with pytest.raises(TTSError, match="No voice loaded"):
            engine.synthesize("Hello world")

    def test_load_voice_missing_file_raises(self, temp_voices_dir):
        """Should raise FileNotFoundError for missing voice"""
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)

        with pytest.raises(FileNotFoundError, match="Voice file not found"):
            engine.load_voice("nonexistent-voice")

    def test_get_current_voice(self, temp_voices_dir, mock_voice_file, mocker):
        """Should return currently loaded voice name"""
        mocker.patch("piper.PiperVoice.load")
        engine = PiperTTSEngine(voices_dir=temp_voices_dir)

        assert engine.current_voice is None

        engine.load_voice("en_US-test-medium")
        assert engine.current_voice == "en_US-test-medium"
