from unittest.mock import MagicMock, patch


@patch("f1p.app.F1PlayerApp")
def test_main(mock_class: MagicMock, mock_f1p_app: MagicMock) -> None:
    mock_class.return_value = mock_f1p_app

    from f1p.main import main

    main()

    mock_class.assert_called_once()
    mock_f1p_app.run.assert_called_once()

