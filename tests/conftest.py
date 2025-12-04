"""Pytest configuration and shared fixtures"""

import pytest


@pytest.fixture
def temp_voices_dir(tmp_path):
    """Create a temporary voices directory for testing"""
    voices_dir = tmp_path / "voices"
    voices_dir.mkdir()
    return voices_dir


@pytest.fixture
def mock_voice_file(temp_voices_dir):
    """Create a mock voice file for testing"""
    import json

    voice_path = temp_voices_dir / "en_US-test-medium.onnx"
    voice_path.touch()

    # Create corresponding JSON config with required fields
    config = {
        "num_symbols": 100,
        "num_speakers": 1,
        "audio": {"sample_rate": 22050},
        "espeak": {"voice": "en-us"},
        "phoneme_id_map": {},
    }
    json_path = temp_voices_dir / "en_US-test-medium.onnx.json"
    json_path.write_text(json.dumps(config))

    return voice_path
