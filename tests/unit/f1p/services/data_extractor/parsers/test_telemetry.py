from unittest.mock import MagicMock

import pytest
from pandas import DataFrame, Timedelta
from pandas._testing import assert_frame_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.parsers.telemetry import TelemetryParser


@pytest.fixture()
def parser(mock_session: MagicMock) -> TelemetryParser:
    return TelemetryParser(mock_session)


def test_initialization(mock_session: MagicMock) -> None:
    parser = TelemetryParser(mock_session)

    assert mock_session == parser.session
    assert parser._car_data is None
    assert parser._processed_car_data is None


def test_car_data_property_fetches_when_none(parser: TelemetryParser, car_data: dict[str, DataFrame]) -> None:
    assert parser._car_data is None

    assert car_data == parser.car_data
    assert parser._car_data is not None
    assert car_data == parser._car_data


def test_car_data_property_caches(parser: TelemetryParser, car_data: dict[str, DataFrame]) -> None:
    assert parser._car_data is None

    assert car_data == parser.car_data, "First time computes"
    assert car_data == parser.car_data, "Second time returns cache"

    assert parser._car_data is not None


def test_processed_car_data_property_returns_set_value(parser: TelemetryParser, processed_car_data: DataFrame) -> None:
    parser._processed_car_data = processed_car_data

    assert_frame_equal(processed_car_data, parser.processed_car_data)


def test_processed_car_data_property_raises_value_error_when_none(parser: TelemetryParser) -> None:
    assert parser._processed_car_data is None

    with pytest.raises(ValueError, match="Car data not processed yet."):
        assert parser.processed_car_data is None


def test_combine_car_data(
    parser: TelemetryParser,
    car_data: dict[str, DataFrame],
    processed_car_data_after_combined_car_data: DataFrame,
) -> None:
    parser._car_data = car_data

    assert parser._processed_car_data is None

    parser._combine_car_data()

    assert_frame_equal(processed_car_data_after_combined_car_data, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_combined_car_data, parser._processed_car_data)


def test_trim_to_session_time(
    parser: TelemetryParser,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_car_data_after_combined_car_data: DataFrame,
    processed_car_data_after_trim_to_session_time: DataFrame,
) -> None:
    parser._processed_car_data = processed_car_data_after_combined_car_data

    parser._trim_to_session_time(session_start_time, session_end_time)

    assert_frame_equal(processed_car_data_after_trim_to_session_time, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_trim_to_session_time, parser._processed_car_data)


def test_add_session_time_ticks(
    parser: TelemetryParser,
    session_time_ticks_df: DataFrame,
    processed_car_data_after_trim_to_session_time: DataFrame,
    processed_car_data_after_add_session_time_ticks: DataFrame,
) -> None:
    parser._processed_car_data = processed_car_data_after_trim_to_session_time

    assert "SessionTimeTick" not in parser.processed_car_data.columns

    parser._add_session_time_ticks(session_time_ticks_df)

    assert "SessionTimeTick" in parser.processed_car_data.columns

    assert_frame_equal(processed_car_data_after_add_session_time_ticks, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_add_session_time_ticks, parser._processed_car_data)


def test_normalize_gear_indicator(
    parser: TelemetryParser,
    processed_car_data_after_add_session_time_ticks: DataFrame,
    processed_car_data_after_normalize_gear_indicator: DataFrame,
) -> None:
    parser._processed_car_data = processed_car_data_after_add_session_time_ticks

    parser._normalize_gear_indicator()

    assert_frame_equal(processed_car_data_after_normalize_gear_indicator, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_normalize_gear_indicator, parser._processed_car_data)


def test_convert_speed_to_mph(
    parser: TelemetryParser,
    processed_car_data_after_normalize_gear_indicator: DataFrame,
    processed_car_data_after_convert_speed_to_mph: DataFrame,
) -> None:
    parser._processed_car_data = processed_car_data_after_normalize_gear_indicator

    assert "SpeedMph" not in parser.processed_car_data.columns

    parser._convert_speed_to_mph()

    assert "SpeedMph" in parser.processed_car_data.columns

    assert_frame_equal(processed_car_data_after_convert_speed_to_mph, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_convert_speed_to_mph, parser._processed_car_data)


def test_clean_up(
    parser: TelemetryParser,
    processed_car_data_after_convert_speed_to_mph: DataFrame,
    processed_car_data_after_clean_up: DataFrame,
) -> None:
    parser._processed_car_data = processed_car_data_after_convert_speed_to_mph

    assert "Date" in parser.processed_car_data.columns
    assert "Source" in parser.processed_car_data.columns
    assert "Time" in parser.processed_car_data.columns
    assert "SessionTime" in parser.processed_car_data.columns

    parser._clean_up()

    assert "Date" not in parser.processed_car_data.columns
    assert "Source" not in parser.processed_car_data.columns
    assert "Time" not in parser.processed_car_data.columns
    assert "SessionTime" not in parser.processed_car_data.columns

    assert_frame_equal(processed_car_data_after_clean_up, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data_after_clean_up, parser._processed_car_data)


def test_parse(
    parser: TelemetryParser,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    session_time_ticks_df: DataFrame,
    car_data: dict[str, DataFrame],
    processed_car_data: DataFrame,
) -> None:
    parser._car_data = car_data

    result = parser.parse(session_start_time, session_end_time, session_time_ticks_df)

    assert_frame_equal(processed_car_data, result)
    assert_frame_equal(processed_car_data, parser.processed_car_data)
    assert parser._processed_car_data is not None
    assert_frame_equal(processed_car_data, parser._processed_car_data)


def test_parse_unit(
    parser: TelemetryParser,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    session_time_ticks_df: DataFrame,
    processed_car_data: DataFrame,
    mocker: MockerFixture,
) -> None:
    parser._processed_car_data = processed_car_data

    mock_ccd = mocker.patch.object(parser, "_combine_car_data", return_value=parser)
    mock_ttst = mocker.patch.object(parser, "_trim_to_session_time", return_value=parser)
    mock_astt = mocker.patch.object(parser, "_add_session_time_ticks", return_value=parser)
    mock_ngi = mocker.patch.object(parser, "_normalize_gear_indicator", return_value=parser)
    mock_cstm = mocker.patch.object(parser, "_convert_speed_to_mph", return_value=parser)
    mock_cu = mocker.patch.object(parser, "_clean_up", return_value=parser)

    result = parser.parse(session_start_time, session_end_time, session_time_ticks_df)

    assert_frame_equal(processed_car_data, result)

    mock_ccd.assert_called_once()
    mock_ttst.assert_called_once_with(session_start_time, session_end_time)
    mock_astt.assert_called_once_with(session_time_ticks_df)
    mock_ngi.assert_called_once()
    mock_cstm.assert_called_once()
    mock_cu.assert_called_once()