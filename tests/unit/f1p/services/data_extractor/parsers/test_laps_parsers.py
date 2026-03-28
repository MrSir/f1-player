from unittest.mock import MagicMock

import pytest
from pandas import DataFrame
from pandas._testing import assert_frame_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.parsers.laps import LapsParser


@pytest.fixture()
def parser(mock_session: MagicMock) -> LapsParser:
    return LapsParser(mock_session, 3)


def test_initialization(mock_session: MagicMock) -> None:
    total_laps = 3
    parser = LapsParser(mock_session, total_laps)

    assert mock_session == parser.session
    assert total_laps == parser.total_laps

    assert parser._laps is None
    assert parser._processed_laps is None

    assert parser._slowest_non_pit_lap is None
    assert parser._fastest_lap is None
    assert parser._end_of_race_milliseconds is None


def test_laps_property_fetches(parser: LapsParser, laps: DataFrame) -> None:
    assert parser._laps is None

    assert_frame_equal(laps, parser.laps)

    assert parser._laps is not None
    assert_frame_equal(laps, parser._laps)


def test_laps_property_caches(parser: LapsParser, laps: DataFrame) -> None:
    assert parser._laps is None

    assert_frame_equal(laps, parser.laps), "First time computes"
    assert_frame_equal(laps, parser.laps), "Second time caches"

    assert parser._laps is not None


def test_processed_laps_data_property_fetches(parser: LapsParser, processed_laps: DataFrame) -> None:
    parser._processed_laps = processed_laps

    assert_frame_equal(processed_laps, parser.processed_laps)


def test_processed_laps_data_property_raises_value_error_when_not_set(parser: LapsParser) -> None:
    parser._processed_laps = None

    with pytest.raises(ValueError, match="Laps not processed yet."):
        assert parser.processed_laps is None


def test_add_total_laps(
    parser: LapsParser,
    laps: DataFrame,
    processed_laps_after_add_total_laps: DataFrame,
) -> None:
    parser._laps = laps

    assert parser._processed_laps is None

    instance = parser._add_total_laps()

    assert isinstance(instance, LapsParser)

    assert parser._processed_laps is not None
    assert "TotalLaps" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_add_total_laps, parser._processed_laps)


def test_convert_sector_session_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_add_total_laps: DataFrame,
    processed_laps_after_convert_sector_session_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_add_total_laps

    for sector in [1, 2, 3]:
        assert f"Sector{sector}SessionTimeMilliseconds" not in parser._processed_laps.columns
        instance = parser._convert_sector_session_time_to_milliseconds(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}SessionTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_sector_session_time_to_milliseconds, parser._processed_laps)


def test_convert_sector_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_sector_session_time_to_milliseconds: DataFrame,
    processed_laps_after_convert_sector_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_sector_session_time_to_milliseconds

    for sector in [1, 2, 3]:
        assert f"Sector{sector}TimeMilliseconds" not in parser._processed_laps.columns
        instance = parser._convert_sector_time_to_milliseconds(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}TimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_sector_time_to_milliseconds, parser._processed_laps)


def test_format_sector_time_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_sector_time_to_milliseconds: DataFrame,
    processed_laps_after_format_sector_time_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_sector_time_to_milliseconds

    for sector in [1, 2, 3]:
        assert f"Sector{sector}TimeFormatted" not in parser._processed_laps.columns
        instance = parser._format_sector_time_milliseconds(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}TimeFormatted" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_format_sector_time_milliseconds, parser._processed_laps)


def test_compute_sector_diff_to_car_ahead(
    parser: LapsParser,
    processed_laps_after_format_sector_time_milliseconds: DataFrame,
    processed_laps_after_compute_sector_diff_to_car_ahead: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_format_sector_time_milliseconds

    for sector in [1, 2, 3]:
        assert f"S{sector}DiffToCarAhead" not in parser._processed_laps.columns
        instance = parser._compute_sector_diff_to_car_ahead(sector)
        assert isinstance(instance, LapsParser)
        assert f"S{sector}DiffToCarAhead" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_sector_diff_to_car_ahead, parser._processed_laps)


def test_compute_sector_time_best(
    parser: LapsParser,
    processed_laps_after_compute_sector_diff_to_car_ahead: DataFrame,
    processed_laps_after_compute_sector_time_best: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_sector_diff_to_car_ahead

    for sector in [1, 2, 3]:
        assert f"Sector{sector}Best" not in parser._processed_laps.columns
        instance = parser._compute_sector_time_best(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}Best" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_sector_time_best, parser._processed_laps)


def test_compute_fastest_sector_time_milliseconds_so_far(
    parser: LapsParser,
    processed_laps_after_compute_sector_time_best: DataFrame,
    processed_laps_after_compute_fastest_sector_time_milliseconds_so_far: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_sector_time_best

    for sector in [1, 2, 3]:
        assert f"FastestSector{sector}TimeMillisecondsSoFar" not in parser._processed_laps.columns
        instance = parser._compute_fastest_sector_time_milliseconds_so_far(sector)
        assert isinstance(instance, LapsParser)
        assert f"FastestSector{sector}TimeMillisecondsSoFar" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_fastest_sector_time_milliseconds_so_far, parser._processed_laps)


def test_compute_sector_color_code(
    parser: LapsParser,
    processed_laps_after_compute_fastest_sector_time_milliseconds_so_far: DataFrame,
    processed_laps_after_compute_sector_color_code: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_fastest_sector_time_milliseconds_so_far

    for sector in [1, 2, 3]:
        assert f"Sector{sector}ColorCode" not in parser._processed_laps.columns
        instance = parser._compute_sector_color_code(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}ColorCode" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_sector_color_code, parser._processed_laps)


def test_add_sector_color(
    parser: LapsParser,
    processed_laps_after_compute_sector_color_code: DataFrame,
    processed_laps_after_compute_sector_color: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_sector_color_code

    for sector in [1, 2, 3]:
        assert f"Sector{sector}Color" not in parser._processed_laps.columns
        instance = parser._add_sector_color(sector)
        assert isinstance(instance, LapsParser)
        assert f"Sector{sector}Color" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_sector_color, parser._processed_laps)


def test_compute_sector_columns(
    parser: LapsParser,
    processed_laps_after_add_total_laps: DataFrame,
    processed_laps_after_compute_sector_columns: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_add_total_laps

    for sector in [1, 2, 3]:
        instance = parser._compute_sector_columns(sector)
        assert isinstance(instance, LapsParser)

    assert_frame_equal(processed_laps_after_compute_sector_columns, parser._processed_laps)


def test_compute_sector_columns_units(parser: LapsParser, mocker: MockerFixture) -> None:
    mock_cssttm = mocker.patch.object(parser, "_convert_sector_session_time_to_milliseconds", return_value=parser)
    mock_csttm = mocker.patch.object(parser, "_convert_sector_time_to_milliseconds", return_value=parser)
    mock_fstm = mocker.patch.object(parser, "_format_sector_time_milliseconds", return_value=parser)
    mock_csdtca = mocker.patch.object(parser, "_compute_sector_diff_to_car_ahead", return_value=parser)
    mock_cstb = mocker.patch.object(parser, "_compute_sector_time_best", return_value=parser)
    mock_cfstmsf = mocker.patch.object(parser, "_compute_fastest_sector_time_milliseconds_so_far", return_value=parser)
    mock_cscc = mocker.patch.object(parser, "_compute_sector_color_code", return_value=parser)
    mock_csc = mocker.patch.object(parser, "_add_sector_color", return_value=parser)

    sector = 1
    instance = parser._compute_sector_columns(sector)
    assert isinstance(instance, LapsParser)

    mock_cssttm.assert_called_once_with(sector)
    mock_csttm.assert_called_once_with(sector)
    mock_fstm.assert_called_once_with(sector)
    mock_csdtca.assert_called_once_with(sector)
    mock_cstb.assert_called_once_with(sector)
    mock_cfstmsf.assert_called_once_with(sector)
    mock_cscc.assert_called_once_with(sector)
    mock_csc.assert_called_once_with(sector)
