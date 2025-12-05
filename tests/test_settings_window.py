"""Tests for SettingsWindow class."""


from src.ui.settings_window import SettingsWindow


class TestSettingsWindow:
    """Test suite for SettingsWindow."""

    def test_voice_dropdown_shows_available_voices(self, mocker):
        """Should populate dropdown with discovered voices."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "en_US-lessac-medium"

        mocker.patch("src.ui.settings_window.tk")
        mock_ttk = mocker.patch("src.ui.settings_window.ttk")

        voices = ["en_US-lessac-medium", "en_US-amy-low", "en_GB-alan-medium"]

        SettingsWindow(mock_settings, voices)

        # Should create combobox with voices
        mock_ttk.Combobox.assert_called()
        call_kwargs = mock_ttk.Combobox.call_args[1]
        assert "values" in call_kwargs
        assert call_kwargs["values"] == voices

    def test_voice_combobox_created(self, mocker):
        """Should create voice combobox widget."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "voice1"

        mocker.patch("src.ui.settings_window.tk")
        mock_ttk = mocker.patch("src.ui.settings_window.ttk")

        SettingsWindow(mock_settings, ["voice1"])

        # Should create Combobox widget
        mock_ttk.Combobox.assert_called()

    def test_save_updates_settings(self, mocker):
        """Should save changes to settings."""
        mock_settings = mocker.Mock()
        mock_settings.get.side_effect = lambda key: {
            "voice": "en_US-lessac-medium",
            "speed": 1.0,
            "output_directory": "~/Downloads",
        }[key]

        mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        window = SettingsWindow(mock_settings, ["en_US-lessac-medium", "en_US-amy-low"])

        # Mock new values
        window._voice_var.get.return_value = "en_US-amy-low"
        window._speed_var.get.return_value = 1.5
        window._output_dir_var.get.return_value = "~/Music"

        # Simulate save button click
        window._on_save()

        # Should update settings (voice, speed, and output_directory)
        assert mock_settings.set.call_count == 3
        mock_settings.save.assert_called_once()

    def test_cancel_closes_without_saving(self, mocker):
        """Should close without saving."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "test_value"

        mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        window = SettingsWindow(mock_settings, ["voice1"])

        # Simulate cancel button click
        window._on_cancel()

        # Should destroy window
        window._window.destroy.assert_called_once()

        # Should not save settings
        mock_settings.save.assert_not_called()

    def test_window_initialization(self, mocker):
        """Should initialize window with correct properties."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "test_value"

        mock_tk = mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")
        mock_window = mocker.Mock()
        mock_tk.Toplevel.return_value = mock_window

        # Mock screen width for positioning calculation
        mock_window.winfo_screenwidth.return_value = 1920

        SettingsWindow(mock_settings, ["voice1"])

        # Should set title
        mock_window.title.assert_called_once_with("Settings")

        # Should set geometry with position
        mock_window.geometry.assert_called_once()
        # Verify geometry string includes position
        geometry_call = mock_window.geometry.call_args[0][0]
        assert "480x320+" in geometry_call  # Should have width x height + x + y format

    def test_output_directory_field_created(self, mocker):
        """Should create output directory entry."""
        mock_settings = mocker.Mock()
        mock_settings.get.side_effect = lambda key: {
            "voice": "en_US-lessac-medium",
            "speed": 1.0,
            "output_directory": "~/Downloads",
        }[key]

        mock_tk = mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        SettingsWindow(mock_settings, ["voice1"])

        # Should create Entry widget for output directory
        mock_tk.Entry.assert_called()

    def test_browse_button_created(self, mocker):
        """Should create browse button for output directory."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "~/Downloads"

        mock_tk = mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        SettingsWindow(mock_settings, ["voice1"])

        # Should create at least 2 buttons (Browse, Save, Cancel)
        assert mock_tk.Button.call_count >= 3

    def test_show_displays_window(self, mocker):
        """Should display the window."""
        mock_settings = mocker.Mock()
        mock_settings.get.return_value = "test_value"

        mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        window = SettingsWindow(mock_settings, ["voice1"])
        window.show()

        # Should call deiconify and focus_force
        window._window.deiconify.assert_called_once()
        window._window.focus_force.assert_called_once()

    def test_loads_current_settings(self, mocker):
        """Should load current settings on init."""
        mock_settings = mocker.Mock()
        mock_settings.get.side_effect = lambda key: {
            "voice": "en_US-amy-low",
            "speed": 1.5,
            "output_directory": "~/Music",
        }[key]

        mocker.patch("src.ui.settings_window.tk")
        mocker.patch("src.ui.settings_window.ttk")

        window = SettingsWindow(mock_settings, ["en_US-lessac-medium", "en_US-amy-low"])

        # Should have called get for each setting (voice, speed, and output_directory)
        assert mock_settings.get.call_count == 3

        # Check that voice variable was set (appears in call_args_list)
        voice_calls = [call for call in window._voice_var.set.call_args_list]
        assert any(call[0][0] == "en_US-amy-low" for call in voice_calls)

        # Check that speed variable was set
        speed_calls = [call for call in window._speed_var.set.call_args_list]
        assert any(call[0][0] == 1.5 for call in speed_calls)

        # Check that output directory variable was set
        output_calls = [call for call in window._output_dir_var.set.call_args_list]
        assert any(call[0][0] == "~/Music" for call in output_calls)
