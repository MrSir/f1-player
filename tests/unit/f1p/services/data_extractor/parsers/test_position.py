from unittest.mock import MagicMock

import pytest
from pandas import DataFrame
from pandas._testing import assert_frame_equal

from f1p.services.data_extractor.parsers.position import PositionParser


@pytest.fixture()
def parser(mock_session: MagicMock) -> PositionParser:
    return PositionParser(mock_session)


def test_initialization(mock_session: MagicMock) -> None:
    parser = PositionParser(mock_session)

    assert mock_session == parser.session
    assert parser._pos_data is None
    assert parser._processed_pos_data is None


def test_pos_data_property_fetches_when_none(parser: PositionParser, pos_data: dict[str, DataFrame]) -> None:
    assert parser._pos_data is None

    assert pos_data == parser.pos_data
    assert parser._pos_data is not None
    assert pos_data == parser._pos_data


def test_pos_data_property_caches(parser: PositionParser, pos_data: dict[str, DataFrame]) -> None:
    assert parser._pos_data is None

    assert pos_data == parser.pos_data, "First time computes"
    assert pos_data == parser.pos_data, "Second time returns cache"

    assert parser._pos_data is not None


def test_processed_pos_data_property_returns_set_value(parser: PositionParser, processed_pos_data: DataFrame) -> None:
    parser._processed_pos_data = processed_pos_data

    assert_frame_equal(processed_pos_data, parser.processed_pos_data)


def test_processed_pos_data_property_raises_value_error_when_none(parser: PositionParser, processed_pos_data: DataFrame) -> None:
    assert parser._processed_pos_data is None

    with pytest.raises(ValueError, match="Position data not processed yet."):
        assert parser.processed_pos_data is None
