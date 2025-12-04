"""Text extraction from URLs and plain text."""

import re
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


class TextExtractor:
    """Extract and clean text from URLs or plain text input."""

    def __init__(self, timeout: int = 30):
        """Initialize TextExtractor.

        Args:
            timeout: Timeout in seconds for HTTP requests
        """
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                         "AppleWebKit/537.36 (KHTML, like Gecko) "
                         "Chrome/91.0.4472.124 Safari/537.36"
        })

    def is_url(self, text: str) -> bool:
        """Check if text is a valid URL.

        Args:
            text: Input string to check

        Returns:
            True if text is a valid URL, False otherwise
        """
        try:
            result = urlparse(text)
            return all([result.scheme, result.netloc]) and result.scheme in ["http", "https"]
        except Exception:
            return False

    def extract(self, input_text: str) -> str:
        """Extract text from URL or return plain text.

        Args:
            input_text: URL or plain text to extract from

        Returns:
            Extracted and cleaned text

        Raises:
            requests.HTTPError: If URL returns error status code
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        if self.is_url(input_text):
            return self._extract_from_url(input_text)
        else:
            return input_text

    def _extract_from_url(self, url: str) -> str:
        """Fetch and extract text from URL.

        Args:
            url: URL to fetch

        Returns:
            Extracted and cleaned text

        Raises:
            requests.HTTPError: If URL returns error status code
            requests.Timeout: If request times out
            requests.RequestException: For other request errors
        """
        response = self.session.get(url, timeout=self.timeout)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")

        # Remove script, style, nav, and other non-content elements
        for element in soup(["script", "style", "nav", "header", "footer", "aside"]):
            element.decompose()

        # Extract text
        text = soup.get_text()

        # Clean whitespace
        text = self._clean_whitespace(text)

        return text

    def _clean_whitespace(self, text: str) -> str:
        """Clean and normalize whitespace in text.

        Args:
            text: Text to clean

        Returns:
            Cleaned text with normalized whitespace
        """
        # Replace multiple spaces with single space
        text = re.sub(r" +", " ", text)

        # Replace multiple newlines with double newline (paragraph break)
        text = re.sub(r"\n\n+", "\n\n", text)

        # Remove leading/trailing whitespace from each line
        lines = [line.strip() for line in text.split("\n")]

        # Remove empty lines at start and end
        while lines and not lines[0]:
            lines.pop(0)
        while lines and not lines[-1]:
            lines.pop()

        return "\n".join(lines)
