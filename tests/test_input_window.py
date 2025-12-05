"""Tests for InputWindow class."""


from src.ui.input_window import InputWindow


class TestInputWindow:
    """Test suite for InputWindow."""

    def test_submit_calls_callback_with_text(self, mocker):
        """Should call callback with entered text."""
        callback = mocker.Mock()
        mocker.patch("src.ui.input_window.tk")

        window = InputWindow(callback)

        # Simulate user entering text
        window._text_area.get.return_value = "https://example.com"

        # Simulate play button click
        window._on_play()

        # Should call callback with text
        callback.assert_called_once_with("https://example.com")

    def test_clipboard_button_pastes_content(self, mocker):
        """Should paste clipboard content to text area."""
        callback = mocker.Mock()
        mock_tk = mocker.patch("src.ui.input_window.tk")

        # Mock clipboard
        mock_window = mocker.Mock()
        mock_window.clipboard_get.return_value = "Clipboard text here"
        mock_tk.Tk.return_value = mock_window

        window = InputWindow(callback)
        window._window = mock_window

        # Simulate clipboard button click
        window._on_paste_clipboard()

        # Should insert clipboard content into text area
        window._text_area.insert.assert_called_with("1.0", "Clipboard text here")

    def test_esc_closes_window(self, mocker):
        """Should close window on ESC key without callback."""
        callback = mocker.Mock()
        mock_tk = mocker.patch("src.ui.input_window.tk")

        window = InputWindow(callback)

        # Verify ESC binding was set
        window._window.bind.assert_any_call('<Escape>', mocker.ANY)

        # Should not call callback when window is destroyed via ESC
        callback.assert_not_called()

    def test_empty_text_does_not_submit(self, mocker):
        """Should not call callback with empty text."""
        callback = mocker.Mock()
        mocker.patch("src.ui.input_window.tk")

        window = InputWindow(callback)

        # Simulate empty text area
        window._text_area.get.return_value = "   "

        # Simulate play button click
        window._on_play()

        # Should not call callback
        callback.assert_not_called()

    def test_show_displays_window(self, mocker):
        """Should display the window."""
        callback = mocker.Mock()
        mocker.patch("src.ui.input_window.tk")

        window = InputWindow(callback)
        window.show()

        # Should call deiconify and focus_force
        window._window.deiconify.assert_called_once()
        window._window.focus_force.assert_called_once()

    def test_window_initialization(self, mocker):
        """Should initialize window with correct properties."""
        callback = mocker.Mock()
        mock_tk = mocker.patch("src.ui.input_window.tk")
        mock_window = mocker.Mock()
        mock_tk.Toplevel.return_value = mock_window

        # Mock screen width for positioning calculation
        mock_window.winfo_screenwidth.return_value = 1920

        InputWindow(callback)

        # Should set title
        mock_window.title.assert_called_once_with("Piper TTS Reader")

        # Should set geometry with position
        mock_window.geometry.assert_called_once()
        # Verify geometry string includes position
        geometry_call = mock_window.geometry.call_args[0][0]
        assert "420x280+" in geometry_call  # Should have width x height + x + y format

    def test_text_area_created(self, mocker):
        """Should create text area widget."""
        callback = mocker.Mock()
        mock_tk = mocker.patch("src.ui.input_window.tk")
        mock_text = mocker.Mock()
        mock_tk.Text.return_value = mock_text

        InputWindow(callback)

        # Should create Text widget
        mock_tk.Text.assert_called_once()

        # Should pack text area
        mock_text.pack.assert_called()

    def test_buttons_created(self, mocker):
        """Should create play, stop, and download buttons."""
        callback = mocker.Mock()
        mock_tk = mocker.patch("src.ui.input_window.tk")
        mock_button = mocker.Mock()
        mock_tk.Button.return_value = mock_button

        InputWindow(callback)

        # Should create 3 buttons (Download, Play, and Stop)
        assert mock_tk.Button.call_count == 3

        # Should pack download and play buttons initially (not stop)
        assert mock_button.pack.call_count == 2
