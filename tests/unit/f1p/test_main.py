from unittest.mock import MagicMock, patch
from importlib import import_module


@patch("f1p.app.F1PlayerApp")
def test_main(mock_class: MagicMock, mock_f1p_app: MagicMock) -> None:
    mock_class.return_value = mock_f1p_app

    import_module("f1p.main")

    mock_class.assert_called_once()
    mock_f1p_app.configure_window.assert_called_once()
    mock_f1p_app.draw_menu.assert_called_once()
    mock_f1p_app.register_ui_components.assert_called_once()
    mock_f1p_app.register_controls.assert_called_once()
    mock_f1p_app.run.assert_called_once()

