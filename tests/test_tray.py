"""Tests for TrayApplication class."""


from src.tray import TrayApplication


class TestTrayApplication:
    """Test suite for TrayApplication."""

    def test_menu_has_required_items(self, mocker):
        """Should have Read Text, speed, play/pause, stop, download, settings, quit."""
        mock_icon = mocker.patch("src.tray.pystray.Icon")

        TrayApplication()

        # Get the menu passed to Icon constructor
        icon_call_kwargs = mock_icon.call_args[1]
        menu = icon_call_kwargs["menu"]

        # Menu should have items
        menu_items = menu._items

        # Should have menu items for:
        # - Read Text
        # - Separator
        # - Speed submenu
        # - Play/Pause
        # - Stop
        # - Download
        # - Separator
        # - Settings
        # - Quit
        assert len(menu_items) == 9

    def test_speed_menu_has_options(self, mocker):
        """Should have speed options from 0.5x to 2.0x."""
        mock_icon = mocker.patch("src.tray.pystray.Icon")

        TrayApplication()

        # Get the menu passed to Icon constructor
        icon_call_kwargs = mock_icon.call_args[1]
        menu = icon_call_kwargs["menu"]
        menu_items = menu._items

        # Find speed submenu (third item after Read Text and separator)
        speed_item = menu_items[2]

        # Speed item should have submenu (check submenu property)
        assert hasattr(speed_item, "submenu")
        speed_submenu = speed_item.submenu

        # Speed submenu should have 6 options (0.5x to 2.0x)
        assert speed_submenu is not None
        speed_options = speed_submenu._items
        assert len(speed_options) == 6

    def test_play_pause_toggles_text(self, mocker):
        """Should show 'Play' when stopped, 'Pause' when playing."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Initially should show "Play"
        assert app._get_play_pause_text() == "Play"

        # After starting playback, should show "Pause"
        app._is_playing = True
        assert app._get_play_pause_text() == "Pause"

        # After pausing, should show "Resume"
        app._is_paused = True
        assert app._get_play_pause_text() == "Resume"

    def test_download_enabled_when_audio_available(self, mocker):
        """Should enable download when audio is available."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Initially no audio
        assert not app._has_audio()

        # After synthesis, should have audio
        app._audio_data = [1, 2, 3]
        app._sample_rate = 22050
        assert app._has_audio()

    def test_download_callback_disabled_when_no_audio(self, mocker):
        """Should return False for download enabled when no audio."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Should be disabled when no audio
        assert not app._download_enabled(None)

        # Should be enabled when audio available
        app._audio_data = [1, 2, 3]
        app._sample_rate = 22050
        assert app._download_enabled(None)

    def test_run_starts_icon(self, mocker):
        """Should start the pystray icon."""
        mock_icon_instance = mocker.Mock()
        mocker.patch("src.tray.pystray.Icon", return_value=mock_icon_instance)
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()
        app.run()

        # Should call icon.run()
        mock_icon_instance.run.assert_called_once()

    def test_quit_stops_icon(self, mocker):
        """Should stop the icon when quit is called."""
        mock_icon_instance = mocker.Mock()
        mocker.patch("src.tray.pystray.Icon", return_value=mock_icon_instance)
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()
        app._icon = mock_icon_instance

        app._quit(None, None)

        # Should call icon.stop()
        mock_icon_instance.stop.assert_called_once()

    def test_speed_change_callback(self, mocker):
        """Should update speed when speed menu item clicked."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Change speed to 1.5x
        app._change_speed(None, None, 1.5)

        # Should update internal state
        assert app._speed == 1.5

    def test_initial_state(self, mocker):
        """Should initialize with correct default state."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Should start in stopped state
        assert not app._is_playing
        assert not app._is_paused
        assert app._speed == 1.0
        assert app._audio_data is None
        assert app._sample_rate is None
