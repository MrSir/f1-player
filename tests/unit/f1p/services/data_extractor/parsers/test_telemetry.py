from unittest.mock import MagicMock

import pytest
from pandas import DataFrame
from pandas._testing import assert_frame_equal

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
