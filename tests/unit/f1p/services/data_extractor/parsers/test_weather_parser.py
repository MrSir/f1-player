from unittest.mock import MagicMock

import pytest
from pandas import DataFrame
from pandas._testing import assert_frame_equal

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
