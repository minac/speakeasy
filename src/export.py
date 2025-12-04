"""Audio export functionality for MP3 conversion."""

import re
from datetime import datetime
from pathlib import Path

import numpy as np
from pydub import AudioSegment


class AudioExporter:
    """Export audio data to MP3 files."""

    def __init__(self, output_directory: str = "~/Downloads"):
        """Initialize AudioExporter.

        Args:
            output_directory: Directory to save exported files
        """
        self.output_directory = Path(output_directory).expanduser()
        self.output_directory.mkdir(parents=True, exist_ok=True)

    def export(
        self, audio_data: np.ndarray, sample_rate: int, text: str
    ) -> str:
        """Export audio data to MP3 file.

        Args:
            audio_data: Audio samples as numpy array (int16)
            sample_rate: Sample rate in Hz
            text: Text that was synthesized (used for filename generation)

        Returns:
            Path to saved MP3 file
        """
        # Generate filename from text
        filename = self._generate_filename(text)
        output_path = self.output_directory / filename

        # Handle filename conflicts
        output_path = self._resolve_conflict(output_path)

        # Convert numpy array to AudioSegment
        audio_segment = AudioSegment(
            audio_data.tobytes(),
            frame_rate=sample_rate,
            sample_width=audio_data.dtype.itemsize,
            channels=1,
        )

        # Export to MP3
        audio_segment.export(str(output_path), format="mp3")

        return str(output_path)

    def _generate_filename(self, text: str) -> str:
        """Generate filename from text.

        Args:
            text: Text to generate filename from

        Returns:
            Sanitized filename with timestamp
        """
        # Take first 5 words
        words = text.split()[:5]
        filename_base = "_".join(words)

        # Sanitize: remove non-alphanumeric characters
        filename_base = re.sub(r"[^\w\s-]", "", filename_base)
        filename_base = re.sub(r"[\s]+", "_", filename_base)

        # Truncate to reasonable length
        filename_base = filename_base[:50]

        # Add timestamp
        timestamp = self._get_timestamp()
        filename = f"{filename_base}_{timestamp}.mp3"

        return filename

    def _get_timestamp(self) -> str:
        """Get current timestamp for filename.

        Returns:
            Timestamp string in format YYYYMMDD_HHMMSS
        """
        return datetime.now().strftime("%Y%m%d_%H%M%S")

    def _resolve_conflict(self, path: Path) -> Path:
        """Resolve filename conflicts by adding suffix.

        Args:
            path: Original file path

        Returns:
            Path that doesn't conflict with existing files
        """
        if not path.exists():
            return path

        # Add suffix
        counter = 1
        stem = path.stem
        suffix = path.suffix
        parent = path.parent

        while True:
            new_path = parent / f"{stem}_{counter}{suffix}"
            if not new_path.exists():
                return new_path
            counter += 1
