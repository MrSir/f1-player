from unittest.mock import MagicMock

import pytest
from pandas import DataFrame, Series, Timedelta
from pandas._testing import assert_frame_equal, assert_series_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.parsers.weather import WeatherParser


@pytest.fixture()
def parser(mock_session: MagicMock) -> WeatherParser:
    return WeatherParser(mock_session)


def test_initialization(mock_session: MagicMock) -> None:
    parser = WeatherParser(mock_session)

    assert mock_session == parser.session

    assert parser._weather_data is None
    assert parser._processed_weather_data is None


def test_weather_data_property_fetches(parser: WeatherParser, weather_data: DataFrame) -> None:
    assert parser._weather_data is None

    assert_frame_equal(weather_data, parser.weather_data)
    assert parser._weather_data is not None
    assert_frame_equal(weather_data, parser._weather_data)


def test_weather_data_property_caches(parser: WeatherParser, weather_data: DataFrame) -> None:
    assert parser._weather_data is None

    assert_frame_equal(weather_data, parser.weather_data), "First time computes"
    assert_frame_equal(weather_data, parser.weather_data), "Second time caches"

    assert parser._weather_data is not None


def test_processed_weather_data_property_fetches(parser: WeatherParser, processed_weather_data: DataFrame) -> None:
    parser._processed_weather_data = processed_weather_data

    assert_frame_equal(processed_weather_data, parser.processed_weather_data)


def test_processed_weather_data_property_raises_value_error_when_not_set(parser: WeatherParser) -> None:
    parser._processed_weather_data = None

    with pytest.raises(ValueError, match="Weather data is not processed yet."):
        assert parser.processed_weather_data is None


def test_trim_to_session_time(
    parser: WeatherParser,
    weather_data: DataFrame,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_weather_data_after_trim_to_session_time: DataFrame,
) -> None:
    parser._weather_data = weather_data

    assert parser._processed_weather_data is None

    instance = parser._trim_to_session_time(session_start_time, session_end_time)

    assert isinstance(instance, WeatherParser)
    assert parser._processed_weather_data is not None

    assert_frame_equal(processed_weather_data_after_trim_to_session_time, parser._processed_weather_data)


def test_add_session_time_ticks(
    parser: WeatherParser,
    processed_weather_data_after_trim_to_session_time: DataFrame,
    session_time_ticks_df: DataFrame,
    processed_weather_data_after_add_session_time_ticks: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_trim_to_session_time

    assert "SessionTimeTick" not in parser._processed_weather_data.columns

    instance = parser._add_session_time_ticks(session_time_ticks_df)

    assert isinstance(instance, WeatherParser)
    assert "SessionTimeTick" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_add_session_time_ticks, parser._processed_weather_data)


def test_convert_air_temp_to_fahrenheit(
    parser: WeatherParser,
    processed_weather_data_after_add_session_time_ticks: DataFrame,
    processed_weather_data_after_convert_air_temp_to_fahrenheit: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_add_session_time_ticks

    assert "AirTempF" not in parser._processed_weather_data.columns

    instance = parser._convert_air_temp_to_fahrenheit()

    assert isinstance(instance, WeatherParser)
    assert "AirTempF" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_convert_air_temp_to_fahrenheit, parser._processed_weather_data)


def test_convert_track_temp_to_fahrenheit(
    parser: WeatherParser,
    processed_weather_data_after_convert_air_temp_to_fahrenheit: DataFrame,
    processed_weather_data_after_convert_track_temp_to_fahrenheit: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_convert_air_temp_to_fahrenheit

    assert "TrackTempF" not in parser._processed_weather_data.columns

    instance = parser._convert_track_temp_to_fahrenheit()

    assert isinstance(instance, WeatherParser)
    assert "TrackTempF" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_convert_track_temp_to_fahrenheit, parser._processed_weather_data)


def test_convert_pressure_to_kilopascal(
    parser: WeatherParser,
    processed_weather_data_after_convert_track_temp_to_fahrenheit: DataFrame,
    processed_weather_data_after_convert_pressure_to_kilopascal: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_convert_track_temp_to_fahrenheit

    instance = parser._convert_pressure_to_kilopascal()

    assert isinstance(instance, WeatherParser)

    assert_frame_equal(processed_weather_data_after_convert_pressure_to_kilopascal, parser._processed_weather_data)


def test_convert_wind_speed_to_km_p_h(
    parser: WeatherParser,
    processed_weather_data_after_convert_pressure_to_kilopascal: DataFrame,
    processed_weather_data_after_convert_wind_speed_to_km_p_h: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_convert_pressure_to_kilopascal

    instance = parser._convert_wind_speed_to_km_p_h()

    assert isinstance(instance, WeatherParser)

    assert_frame_equal(processed_weather_data_after_convert_wind_speed_to_km_p_h, parser._processed_weather_data)


def test_add_weather_symbol(
    parser: WeatherParser,
    processed_weather_data_after_convert_wind_speed_to_km_p_h: DataFrame,
    processed_weather_data_after_add_weather_symbol: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_convert_wind_speed_to_km_p_h

    assert "WeatherSymbol" not in parser._processed_weather_data.columns

    instance = parser._add_weather_symbol()

    assert isinstance(instance, WeatherParser)
    assert "WeatherSymbol" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_add_weather_symbol, parser._processed_weather_data)


def test_add_weather_text(
    parser: WeatherParser,
    processed_weather_data_after_add_weather_symbol: DataFrame,
    processed_weather_data_after_add_weather_text: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_add_weather_symbol

    assert "WeatherText" not in parser._processed_weather_data.columns

    instance = parser._add_weather_text()

    assert isinstance(instance, WeatherParser)
    assert "WeatherText" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_add_weather_text, parser._processed_weather_data)


def test_add_wind_direction_symbol(
    parser: WeatherParser,
    processed_weather_data_after_add_weather_text: DataFrame,
    processed_weather_data_after_add_wind_direction_symbol: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_add_weather_text

    assert "WindDirectionSymbol" not in parser._processed_weather_data.columns

    instance = parser._add_wind_direction_symbol()

    assert isinstance(instance, WeatherParser)
    assert "WindDirectionSymbol" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data_after_add_wind_direction_symbol, parser._processed_weather_data)


def test_add_wind_direction_text(
    parser: WeatherParser,
    processed_weather_data_after_add_wind_direction_symbol: DataFrame,
    processed_weather_data: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data_after_add_wind_direction_symbol

    assert "WindDirectionText" not in parser._processed_weather_data.columns

    instance = parser._add_wind_direction_text()

    assert isinstance(instance, WeatherParser)
    assert "WindDirectionText" in parser._processed_weather_data.columns

    assert_frame_equal(processed_weather_data, parser._processed_weather_data)


def test_process_weather_data(
    parser: WeatherParser,
    weather_data: DataFrame,
    session_time_ticks_df: DataFrame,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_weather_data: DataFrame,
) -> None:
    parser._weather_data = weather_data
    assert parser._processed_weather_data is None

    parser.process_weather_data(session_time_ticks_df, session_start_time, session_end_time)

    assert parser._processed_weather_data is not None

    assert_frame_equal(processed_weather_data, parser._processed_weather_data)


def test_process_weather_data_unit(
    parser: WeatherParser,
    weather_data: DataFrame,
    session_time_ticks_df: DataFrame,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    mocker: MockerFixture,
) -> None:
    parser._weather_data = weather_data
    assert parser._processed_weather_data is None

    mock_ttss = mocker.patch.object(parser, "_trim_to_session_time", return_value=parser)
    mock_astt = mocker.patch.object(parser, "_add_session_time_ticks", return_value=parser)
    mock_cattf = mocker.patch.object(parser, "_convert_air_temp_to_fahrenheit", return_value=parser)
    mock_ctttf = mocker.patch.object(parser, "_convert_track_temp_to_fahrenheit", return_value=parser)
    mock_cptk = mocker.patch.object(parser, "_convert_pressure_to_kilopascal", return_value=parser)
    mock_cwstkph = mocker.patch.object(parser, "_convert_wind_speed_to_km_p_h", return_value=parser)
    mock_aws = mocker.patch.object(parser, "_add_weather_symbol", return_value=parser)
    mock_awt = mocker.patch.object(parser, "_add_weather_text", return_value=parser)
    mock_awds = mocker.patch.object(parser, "_add_wind_direction_symbol", return_value=parser)
    mock_awdt = mocker.patch.object(parser, "_add_wind_direction_text", return_value=parser)

    parser.process_weather_data(session_time_ticks_df, session_start_time, session_end_time)

    mock_ttss.assert_called_once_with(session_start_time, session_end_time)
    mock_astt.assert_called_once_with(session_time_ticks_df)
    mock_cattf.assert_called_once()
    mock_ctttf.assert_called_once()
    mock_cptk.assert_called_once()
    mock_cwstkph.assert_called_once()
    mock_aws.assert_called_once()
    mock_awt.assert_called_once()
    mock_awds.assert_called_once()
    mock_awdt.assert_called_once()


def test_get_current_weather_data(
    parser: WeatherParser,
    processed_weather_data: DataFrame,
    processed_weather_data_at_tick_2: Series,
) -> None:
    parser._processed_weather_data = processed_weather_data

    result = parser.get_current_weather_data(2)

    assert result is not None

    assert_series_equal(processed_weather_data_at_tick_2, result)


def test_get_current_weather_data_returns_none(
    parser: WeatherParser,
    processed_weather_data: DataFrame,
) -> None:
    parser._processed_weather_data = processed_weather_data

    result = parser.get_current_weather_data(1)

    assert result is None
