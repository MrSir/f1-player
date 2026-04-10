from direct.showbase.ShowBase import ShowBase
from pytest_mock import MockerFixture


def test_initialization(mocker: MockerFixture):
    mock_super = mocker.MagicMock()
    mocker.patch("f1p.app.super", return_value=mock_super)

    from f1p.app import F1PlayerApp
    app = F1PlayerApp()

    assert isinstance(app, ShowBase)

    assert 800 == app.width
    assert 800 == app.height
    assert app.show_frame_rate is False
    assert app.pstat_debug is False
    assert [] == app.ui_components

    assert app._symbols_font is None
    assert app._text_font is None
    assert app._session_parser is None
    assert app._data_extractor is None
