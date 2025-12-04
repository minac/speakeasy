"""Tests for AudioExporter class."""

from pathlib import Path

import numpy as np

from src.export import AudioExporter


class TestAudioExporter:
    """Test suite for AudioExporter."""

    def test_export_creates_mp3_file(self, tmp_path, mocker):
        """Should create MP3 file from audio data."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Mock pydub AudioSegment
        mock_segment = mocker.Mock()
        mock_audio_segment_class = mocker.patch("src.export.AudioSegment")
        mock_audio_segment_class.return_value = mock_segment

        exporter = AudioExporter(output_directory=str(output_dir))
        audio_data = np.array([100, 200, 300], dtype=np.int16)
        sample_rate = 22050

        result_path = exporter.export(audio_data, sample_rate, "Test text")

        # Should call AudioSegment with correct parameters
        mock_audio_segment_class.assert_called_once()
        # Should call export on the segment
        mock_segment.export.assert_called_once()
        # Should return path to file
        assert result_path.endswith(".mp3")

    def test_export_uses_settings_directory(self, tmp_path, mocker):
        """Should save to configured output directory."""
        output_dir = tmp_path / "custom_output"
        output_dir.mkdir()

        mock_segment = mocker.Mock()
        mock_audio_segment_class = mocker.patch("src.export.AudioSegment")
        mock_audio_segment_class.return_value = mock_segment

        exporter = AudioExporter(output_directory=str(output_dir))
        audio_data = np.array([100, 200, 300], dtype=np.int16)
        sample_rate = 22050

        result_path = exporter.export(audio_data, sample_rate, "Test")

        # Result path should be in the custom directory
        assert str(output_dir) in result_path

    def test_export_generates_filename(self, tmp_path, mocker):
        """Should generate readable filename from text."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        mock_segment = mocker.Mock()
        mock_audio_segment_class = mocker.patch("src.export.AudioSegment")
        mock_audio_segment_class.return_value = mock_segment

        exporter = AudioExporter(output_directory=str(output_dir))
        audio_data = np.array([100, 200, 300], dtype=np.int16)
        sample_rate = 22050

        result_path = exporter.export(
            audio_data, sample_rate, "Hello world this is a test"
        )

        # Should contain sanitized text from first few words
        filename = Path(result_path).name
        assert "hello" in filename.lower() or "test" in filename.lower()
        assert filename.endswith(".mp3")

    def test_export_handles_filename_conflict(self, tmp_path, mocker):
        """Should add suffix for duplicate filenames."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        # Create a mock that actually creates the file
        def mock_export(path, format):
            Path(path).touch()

        mock_segment = mocker.Mock()
        mock_segment.export.side_effect = mock_export
        mock_audio_segment_class = mocker.patch("src.export.AudioSegment")
        mock_audio_segment_class.return_value = mock_segment

        exporter = AudioExporter(output_directory=str(output_dir))
        audio_data = np.array([100, 200, 300], dtype=np.int16)
        sample_rate = 22050

        # Mock timestamp to ensure same filename
        fixed_timestamp = "20250101_120000"
        mocker.patch.object(
            exporter, "_get_timestamp", return_value=fixed_timestamp
        )

        # Export twice with same text
        path1 = exporter.export(audio_data, sample_rate, "Same text")
        path2 = exporter.export(audio_data, sample_rate, "Same text")

        # Paths should be different
        assert path1 != path2
        # Second should have suffix
        assert "_1.mp3" in path2

    def test_export_returns_file_path(self, tmp_path, mocker):
        """Should return path to saved file."""
        output_dir = tmp_path / "output"
        output_dir.mkdir()

        mock_segment = mocker.Mock()
        mock_audio_segment_class = mocker.patch("src.export.AudioSegment")
        mock_audio_segment_class.return_value = mock_segment

        exporter = AudioExporter(output_directory=str(output_dir))
        audio_data = np.array([100, 200, 300], dtype=np.int16)
        sample_rate = 22050

        result_path = exporter.export(audio_data, sample_rate, "Test")

        # Should return a string path
        assert isinstance(result_path, str)
        assert result_path.endswith(".mp3")
        assert str(output_dir) in result_path
