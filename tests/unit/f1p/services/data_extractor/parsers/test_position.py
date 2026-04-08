import math
from unittest.mock import MagicMock

import pytest
from pandas import DataFrame, Timedelta
from pandas._testing import assert_frame_equal
from pytest_mock import MockerFixture

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


def test_processed_pos_data_property_raises_value_error_when_none(parser: PositionParser) -> None:
    assert parser._processed_pos_data is None

    with pytest.raises(ValueError, match="Position data not processed yet."):
        assert parser.processed_pos_data is None


def test_lowest_z_coordinate_property_fetches_when_none(parser: PositionParser, processed_pos_data: DataFrame) -> None:
    parser._processed_pos_data = processed_pos_data

    assert parser._lowest_z_coordinate is None

    assert pytest.approx(-1.3983333333333332) == parser.lowest_z_coordinate

    assert parser._lowest_z_coordinate is not None
    assert pytest.approx(-1.3983333333333332) == parser._lowest_z_coordinate


def test_lowest_z_coordinate_property_caches(parser: PositionParser, processed_pos_data: DataFrame) -> None:
    parser._processed_pos_data = processed_pos_data

    assert parser._lowest_z_coordinate is None

    assert pytest.approx(-1.3983333333333332) == parser.lowest_z_coordinate, "First time computes"
    assert pytest.approx(-1.3983333333333332) == parser.lowest_z_coordinate, "Second time returns cache"

    assert parser._lowest_z_coordinate is not None


def test_combine_position_data(
    parser: PositionParser,
    pos_data: dict[str, DataFrame],
    combined_pos_data: DataFrame,
) -> None:
    parser._pos_data = pos_data

    assert parser._processed_pos_data is None

    parser._combine_position_data()

    assert_frame_equal(combined_pos_data, parser.processed_pos_data)
    assert parser._processed_pos_data is not None
    assert_frame_equal(combined_pos_data, parser._processed_pos_data)


def test_remove_records_before_session_start_time(
    parser: PositionParser,
    session_start_time: Timedelta,
    combined_pos_data: DataFrame,
    processed_pos_data_after_remove_records_before_session_start_time: DataFrame,
) -> None:
    parser._processed_pos_data = combined_pos_data

    parser._remove_records_before_session_start_time(session_start_time)

    assert_frame_equal(processed_pos_data_after_remove_records_before_session_start_time, parser.processed_pos_data)
    assert_frame_equal(processed_pos_data_after_remove_records_before_session_start_time, parser._processed_pos_data)


def test_normalize_position_data(
    parser: PositionParser,
    processed_pos_data_after_remove_records_before_session_start_time: DataFrame,
    processed_pos_data_after_normalize_position_data: DataFrame,
) -> None:
    parser._processed_pos_data = processed_pos_data_after_remove_records_before_session_start_time

    map_rotation = math.pi / 3
    map_center_coordinate = (1.2, 1.3, 1.4)

    parser._normalize_position_data(map_rotation, map_center_coordinate)

    assert_frame_equal(processed_pos_data_after_normalize_position_data, parser.processed_pos_data)
    assert_frame_equal(processed_pos_data_after_normalize_position_data, parser._processed_pos_data)


def test_add_session_time_in_milliseconds(
    parser: PositionParser,
    processed_pos_data_after_normalize_position_data: DataFrame,
    processed_pos_data_after_add_session_time_in_milliseconds: DataFrame,
) -> None:
    parser._processed_pos_data = processed_pos_data_after_normalize_position_data

    parser._add_session_time_in_milliseconds()

    assert_frame_equal(processed_pos_data_after_add_session_time_in_milliseconds, parser.processed_pos_data)
    assert_frame_equal(processed_pos_data_after_add_session_time_in_milliseconds, parser._processed_pos_data)


def test_add_session_time_tick(
    parser: PositionParser,
    processed_pos_data_after_add_session_time_in_milliseconds: DataFrame,
    processed_pos_data_after_add_session_time_tick: DataFrame,
) -> None:
    parser._processed_pos_data = processed_pos_data_after_add_session_time_in_milliseconds

    parser._add_session_time_tick()

    assert_frame_equal(processed_pos_data_after_add_session_time_tick, parser.processed_pos_data)
    assert_frame_equal(processed_pos_data_after_add_session_time_tick, parser._processed_pos_data)


def test_parse(
    parser: PositionParser,
    session_start_time: Timedelta,
    pos_data: dict[str, DataFrame],
    processed_pos_data: DataFrame,
) -> None:
    parser._pos_data = pos_data

    map_rotation = math.pi / 3
    map_center_coordinate = (1.2, 1.3, 1.4)

    result = parser.parse(session_start_time, map_rotation, map_center_coordinate)

    assert_frame_equal(processed_pos_data, result)
    assert_frame_equal(processed_pos_data, parser.processed_pos_data)
    assert_frame_equal(processed_pos_data, parser._processed_pos_data)


def test_parse_units(
    parser: PositionParser,
    session_start_time: Timedelta,
    processed_pos_data: DataFrame,
    mocker: MockerFixture,
) -> None:
    parser._processed_pos_data = processed_pos_data

    mock_cpd = mocker.patch.object(parser, '_combine_position_data', return_value=parser)
    mock_rrbsst = mocker.patch.object(parser, '_remove_records_before_session_start_time', return_value=parser)
    mock_npd = mocker.patch.object(parser, '_normalize_position_data', return_value=parser)
    mock_astim = mocker.patch.object(parser, '_add_session_time_in_milliseconds', return_value=parser)
    mock_astt = mocker.patch.object(parser, '_add_session_time_tick', return_value=parser)

    map_rotation = math.pi / 3
    map_center_coordinate = (1.2, 1.3, 1.4)

    result = parser.parse(session_start_time, map_rotation, map_center_coordinate)

    assert_frame_equal(processed_pos_data, result)
    assert_frame_equal(processed_pos_data, parser.processed_pos_data)

    mock_cpd.assert_called_once()
    mock_rrbsst.assert_called_once_with(session_start_time)
    mock_npd.assert_called_once_with(map_rotation, map_center_coordinate)
    mock_astim.assert_called_once()
    mock_astt.assert_called_once()
