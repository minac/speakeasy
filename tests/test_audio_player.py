"""Tests for Audio Player"""


import numpy as np
import pytest

from src.audio_player import AudioPlayer, PlaybackState


class TestAudioPlayer:
    @pytest.fixture
    def audio_data(self):
        """Create sample audio data for testing"""
        # Generate 0.5 seconds of audio at 22050 Hz
        sample_rate = 22050
        duration = 0.5
        samples = int(sample_rate * duration)
        # Simple sine wave
        t = np.linspace(0, duration, samples)
        frequency = 440  # A4 note
        audio = (np.sin(2 * np.pi * frequency * t) * 32767).astype(np.int16)
        return audio

    @pytest.fixture
    def player(self):
        """Create an AudioPlayer instance"""
        return AudioPlayer(sample_rate=22050)

    def test_initial_state_is_stopped(self, player):
        """Should start in stopped state"""
        assert player.state == PlaybackState.STOPPED

    def test_play_starts_playback(self, player, audio_data, mocker):
        """Should start playing audio"""
        # Mock sounddevice
        mock_output_stream = mocker.patch("sounddevice.OutputStream")

        player.play(audio_data)

        assert player.state == PlaybackState.PLAYING
        mock_output_stream.assert_called_once()

    def test_pause_stops_playback_temporarily(self, player, audio_data, mocker):
        """Should pause without losing position"""
        mock_stream = mocker.MagicMock()
        mocker.patch("sounddevice.OutputStream", return_value=mock_stream)

        player.play(audio_data)
        player.pause()

        assert player.state == PlaybackState.PAUSED
        mock_stream.stop.assert_called_once()

    def test_resume_continues_from_pause_position(self, player, audio_data, mocker):
        """Should continue from where it paused"""
        mock_stream = mocker.MagicMock()
        mocker.patch("sounddevice.OutputStream", return_value=mock_stream)

        player.play(audio_data)
        player.pause()
        player.resume()

        assert player.state == PlaybackState.PLAYING
        # Stream should be started again
        assert mock_stream.start.call_count >= 1

    def test_stop_resets_position(self, player, audio_data, mocker):
        """Should stop and reset to beginning"""
        mock_stream = mocker.MagicMock()
        mocker.patch("sounddevice.OutputStream", return_value=mock_stream)

        player.play(audio_data)
        player.stop()

        assert player.state == PlaybackState.STOPPED
        assert player.position == 0
        mock_stream.stop.assert_called_once()
        mock_stream.close.assert_called_once()

    def test_state_transitions(self, player, audio_data, mocker):
        """Should correctly track playing/paused/stopped states"""
        mocker.patch("sounddevice.OutputStream")

        # Initial state
        assert player.state == PlaybackState.STOPPED

        # Play
        player.play(audio_data)
        assert player.state == PlaybackState.PLAYING

        # Pause
        player.pause()
        assert player.state == PlaybackState.PAUSED

        # Resume
        player.resume()
        assert player.state == PlaybackState.PLAYING

        # Stop
        player.stop()
        assert player.state == PlaybackState.STOPPED

    def test_speed_change_during_playback(self, player, audio_data, mocker):
        """Should adjust speed without restarting"""
        mocker.patch("sounddevice.OutputStream")

        player.play(audio_data)
        initial_speed = player.speed

        player.set_speed(1.5)

        assert player.speed == 1.5
        assert player.speed != initial_speed
        # Should still be playing
        assert player.state == PlaybackState.PLAYING

    def test_completion_callback_called(self, player, audio_data, mocker):
        """Should call callback when playback finishes"""
        callback = mocker.MagicMock()
        mocker.patch("sounddevice.OutputStream")

        player.set_completion_callback(callback)
        player.play(audio_data)

        # Simulate completion by calling the internal callback
        player._on_completion()

        callback.assert_called_once()
        assert player.state == PlaybackState.STOPPED

    def test_play_while_playing_restarts(self, player, audio_data, mocker):
        """Should restart playback when play called while playing"""
        mock_stream = mocker.MagicMock()
        mocker.patch("sounddevice.OutputStream", return_value=mock_stream)

        player.play(audio_data)
        player.play(audio_data)

        # Should have stopped and started a new stream
        assert mock_stream.stop.call_count >= 1
        assert player.state == PlaybackState.PLAYING

    def test_pause_when_not_playing_does_nothing(self, player):
        """Should handle pause when not playing"""
        # Should not raise an error
        player.pause()
        assert player.state == PlaybackState.STOPPED

    def test_resume_when_not_paused_does_nothing(self, player):
        """Should handle resume when not paused"""
        # Should not raise an error
        player.resume()
        assert player.state == PlaybackState.STOPPED

    def test_get_position(self, player, audio_data, mocker):
        """Should return current playback position"""
        mocker.patch("sounddevice.OutputStream")

        assert player.position == 0

        player.play(audio_data)
        # Position should be tracked (we'll just verify it exists)
        assert player.position >= 0

    def test_get_duration(self, player, audio_data, mocker):
        """Should return total audio duration"""
        mocker.patch("sounddevice.OutputStream")

        player.play(audio_data)
        duration = player.duration

        assert duration > 0
        # Duration should match audio length
        expected_duration = len(audio_data) / player.sample_rate
        assert abs(duration - expected_duration) < 0.01
