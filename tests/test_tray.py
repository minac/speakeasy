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


    def test_tray_app_initializes(self, mocker):
        """Should initialize tray app correctly."""
        mocker.patch("src.tray.pystray.Icon")
        mocker.patch("src.tray.pystray.Menu")

        app = TrayApplication()

        # Verify tray app is initialized
        assert app._icon is not None


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

        # Should initialize with icon
        assert app._icon is not None
