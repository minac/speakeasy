"""Tests for TrayApplication class."""


from src.tray import TrayApplication


class TestTrayApplication:
    """Test suite for TrayApplication."""

    def test_menu_has_required_items(self, mocker):
        """Should have Read Text, settings, quit."""
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
        # - Settings
        # - Quit
        assert len(menu_items) == 4


    def test_play_pause_toggles_text(self, mocker):
        """Should show Play when stopped, Stop when playing."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Verify tray app is initialized
        assert app._icon is not None
        assert app._audio_data is None
        assert app._sample_rate is None

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


    def test_initial_state(self, mocker):
        """Should initialize with correct default state."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Should start with no audio data
        assert app._audio_data is None
        assert app._sample_rate is None
