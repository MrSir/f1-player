from unittest.mock import MagicMock

from direct.gui.DirectButton import DirectButton
from pytest_mock import MockerFixture

from f1p.ui.components.gui.button import BlackButton


def test_initialization(mock_parent: MagicMock, mocker: MockerFixture) -> None:
    mock_defineoptions = mocker.MagicMock(return_value=None)
    mocker.patch("f1p.ui.components.gui.button.DirectButton.defineoptions", mock_defineoptions)
    mock_init = mocker.MagicMock(return_value=None)
    mocker.patch("f1p.ui.components.gui.button.DirectButton.__init__", mock_init)
    mock_initialiseoptions = mocker.MagicMock(return_value=None)
    mocker.patch("f1p.ui.components.gui.button.DirectButton.initialiseoptions", mock_initialiseoptions)

    kwargs = {"a": 1, "b": 2}
    button = BlackButton(mock_parent, **kwargs)

    assert isinstance(button, DirectButton)
    mock_defineoptions.assert_called_once_with(
        kwargs,
        (
            ('frameColor', (0.15, 0.15, 0.15, 1), None),
            ('relief', 2, None),
            ('borderWidth', (3, 3), None),
            ('pressEffect', 1, None),
            ('text_fg', (1, 1, 1, 1), None),
        )
    )
    mock_init.assert_called_once_with(button, mock_parent, **kwargs)
    mock_initialiseoptions.assert_called_once_with(BlackButton)
