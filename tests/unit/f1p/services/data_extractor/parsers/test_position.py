from unittest.mock import MagicMock

from f1p.services.data_extractor.parsers.position import PositionParser


def test_initialization(mock_session: MagicMock) -> None:
    parser = PositionParser(mock_session)

    assert mock_session == parser.session
    assert parser._pos_data is None
    assert parser._processed_pos_data is None
