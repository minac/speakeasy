"""Tests for TextExtractor class."""

import pytest
import requests

from src.text_extractor import TextExtractor


class TestTextExtractor:
    """Test suite for TextExtractor."""

    def test_detect_url_valid(self):
        """Should identify valid URLs."""
        extractor = TextExtractor()
        assert extractor.is_url("https://example.com") is True
        assert extractor.is_url("http://example.com") is True
        assert extractor.is_url("https://en.wikipedia.org/wiki/Test") is True

    def test_detect_url_plain_text(self):
        """Should identify plain text as non-URL."""
        extractor = TextExtractor()
        assert extractor.is_url("Hello world") is False
        assert extractor.is_url("This is plain text") is False
        assert extractor.is_url("example.com") is False  # No protocol

    def test_extract_from_url_returns_text(self, mocker):
        """Should fetch and extract text from URL."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <h1>Title</h1>
                <p>This is the main content.</p>
            </body>
        </html>
        """

        extractor = TextExtractor()
        mocker.patch.object(extractor.session, "get", return_value=mock_response)

        text = extractor.extract("https://example.com")

        assert "Title" in text
        assert "This is the main content." in text

    def test_extract_removes_scripts_and_styles(self, mocker):
        """Should remove non-content elements."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <head>
                <style>body { color: red; }</style>
            </head>
            <body>
                <script>alert('test');</script>
                <p>Main content</p>
                <nav>Navigation</nav>
            </body>
        </html>
        """

        extractor = TextExtractor()
        mocker.patch.object(extractor.session, "get", return_value=mock_response)

        text = extractor.extract("https://example.com")

        assert "Main content" in text
        assert "alert" not in text
        assert "color: red" not in text

    def test_extract_plain_text_passthrough(self):
        """Should return plain text unchanged."""
        extractor = TextExtractor()
        plain_text = "This is plain text to read."
        result = extractor.extract(plain_text)

        assert result == plain_text

    def test_extract_url_not_found_raises(self, mocker):
        """Should raise for 404 responses."""
        mock_response = mocker.Mock()
        mock_response.status_code = 404
        mock_response.raise_for_status.side_effect = requests.HTTPError("404 Not Found")

        extractor = TextExtractor()
        mocker.patch.object(extractor.session, "get", return_value=mock_response)

        with pytest.raises(requests.HTTPError):
            extractor.extract("https://example.com/notfound")

    def test_extract_timeout_raises(self, mocker):
        """Should raise for timeout."""
        extractor = TextExtractor()
        mocker.patch.object(
            extractor.session,
            "get",
            side_effect=requests.Timeout("Connection timeout")
        )

        with pytest.raises(requests.Timeout):
            extractor.extract("https://example.com")

    def test_extract_cleans_whitespace(self, mocker):
        """Should normalize excessive whitespace."""
        mock_response = mocker.Mock()
        mock_response.status_code = 200
        mock_response.text = """
        <html>
            <body>
                <p>Line   with    multiple     spaces</p>
                <p>


                Multiple newlines


                </p>
            </body>
        </html>
        """

        extractor = TextExtractor()
        mocker.patch.object(extractor.session, "get", return_value=mock_response)

        text = extractor.extract("https://example.com")

        # Should not have multiple consecutive spaces or excessive newlines
        assert "   " not in text
        assert "\n\n\n" not in text
