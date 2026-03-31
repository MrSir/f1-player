from unittest.mock import MagicMock

import pytest
from pandas import DataFrame, Series
from pandas._testing import assert_frame_equal, assert_series_equal
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


def test_covert_lap_start_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_compute_sector_columns: DataFrame,
    processed_laps_after_convert_lap_start_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_sector_columns

    assert "LapStartTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._convert_lap_start_time_to_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapStartTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_lap_start_time_to_milliseconds, parser._processed_laps)


def test_covert_lap_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_lap_start_time_to_milliseconds: DataFrame,
    processed_laps_after_convert_lap_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_lap_start_time_to_milliseconds

    assert "LapTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._convert_lap_time_to_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_lap_time_to_milliseconds, parser._processed_laps)


def test_format_lap_time_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_lap_time_to_milliseconds: DataFrame,
    processed_laps_after_format_lap_time_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_lap_time_to_milliseconds

    assert "LapTimeFormatted" not in parser._processed_laps.columns

    instance = parser._format_lap_time_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapTimeFormatted" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_format_lap_time_milliseconds, parser._processed_laps)


def test_compute_lap_end_time_milliseconds(
    parser: LapsParser,
    processed_laps_after_format_lap_time_milliseconds: DataFrame,
    processed_laps_after_compute_lap_end_time_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_format_lap_time_milliseconds

    assert "LapEndTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._compute_lap_end_time_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapEndTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_end_time_milliseconds, parser._processed_laps)


def test_convert_pit_in_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_compute_lap_end_time_milliseconds: DataFrame,
    processed_laps_after_convert_pit_in_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_end_time_milliseconds

    assert "PitInTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._convert_pit_in_time_to_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "PitInTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_pit_in_time_to_milliseconds, parser._processed_laps)


def test_convert_pit_out_time_to_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_pit_in_time_to_milliseconds: DataFrame,
    processed_laps_after_convert_pit_out_time_to_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_pit_in_time_to_milliseconds

    assert "PitOutTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._convert_pit_out_time_to_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "PitOutTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_convert_pit_out_time_to_milliseconds, parser._processed_laps)


def test_add_last_lap_time_milliseconds(
    parser: LapsParser,
    processed_laps_after_convert_pit_out_time_to_milliseconds: DataFrame,
    processed_laps_after_add_last_lap_time_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_convert_pit_out_time_to_milliseconds

    assert "LastLapTimeMilliseconds" not in parser._processed_laps.columns

    instance = parser._add_last_lap_time_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LastLapTimeMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_add_last_lap_time_milliseconds, parser._processed_laps)


def test_add_fastest_lap_time_milliseconds_so_far(
    parser: LapsParser,
    processed_laps_after_add_last_lap_time_milliseconds: DataFrame,
    processed_laps_after_add_fastest_lap_time_milliseconds_so_far: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_add_last_lap_time_milliseconds

    assert "FastestLapTimeMillisecondsSoFar" not in parser._processed_laps.columns

    instance = parser._add_fastest_lap_time_milliseconds_so_far()
    assert isinstance(instance, LapsParser)

    assert "FastestLapTimeMillisecondsSoFar" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_add_fastest_lap_time_milliseconds_so_far, parser._processed_laps)


def test_fill_in_compound(
    parser: LapsParser,
    processed_laps_after_add_fastest_lap_time_milliseconds_so_far: DataFrame,
    processed_laps_after_fill_in_compound: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_add_fastest_lap_time_milliseconds_so_far

    instance = parser._fill_in_compound()
    assert isinstance(instance, LapsParser)

    assert_frame_equal(processed_laps_after_fill_in_compound, parser._processed_laps)


def test_add_compound_color(
    parser: LapsParser,
    processed_laps_after_fill_in_compound: DataFrame,
    processed_laps_after_add_compound_color: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_fill_in_compound

    assert "CompoundColor" not in parser._processed_laps.columns

    instance = parser._add_compound_color()
    assert isinstance(instance, LapsParser)

    assert "CompoundColor" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_add_compound_color, parser._processed_laps)


def test_compute_lap_time_best_milliseconds(
    parser: LapsParser,
    processed_laps_after_add_compound_color: DataFrame,
    processed_laps_after_compute_lap_time_best_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_add_compound_color

    assert "LapTimeBestMilliseconds" not in parser._processed_laps.columns

    instance = parser._compute_lap_time_best_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapTimeBestMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_time_best_milliseconds, parser._processed_laps)


def test_compute_lap_time_personal_best_milliseconds(
    parser: LapsParser,
    processed_laps_after_compute_lap_time_best_milliseconds: DataFrame,
    processed_laps_after_compute_lap_time_personal_best_milliseconds: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_time_best_milliseconds

    assert "LapTimePersonalBestMilliseconds" not in parser._processed_laps.columns

    instance = parser._compute_lap_time_personal_best_milliseconds()
    assert isinstance(instance, LapsParser)

    assert "LapTimePersonalBestMilliseconds" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_time_personal_best_milliseconds, parser._processed_laps)


def test_compute_lap_time_color_code(
    parser: LapsParser,
    processed_laps_after_compute_lap_time_personal_best_milliseconds: DataFrame,
    processed_laps_after_compute_lap_time_color_code: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_time_personal_best_milliseconds

    assert "LapTimeColorCode" not in parser._processed_laps.columns

    instance = parser._compute_lap_time_color_code()
    assert isinstance(instance, LapsParser)

    assert "LapTimeColorCode" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_time_color_code, parser._processed_laps)


def test_compute_lap_time_color(
    parser: LapsParser,
    processed_laps_after_compute_lap_time_color_code: DataFrame,
    processed_laps_after_compute_lap_time_color: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_time_color_code

    assert "LapTimeColor" not in parser._processed_laps.columns

    instance = parser._compute_lap_time_color()
    assert isinstance(instance, LapsParser)

    assert "LapTimeColor" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_time_color, parser._processed_laps)


def test_compute_lap_time_ratio(
    parser: LapsParser,
    processed_laps_after_compute_lap_time_color: DataFrame,
    processed_laps_after_compute_lap_time_ratio: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_time_color

    assert "LapTimeRatio" not in parser._processed_laps.columns

    instance = parser._compute_lap_time_ratio()
    assert isinstance(instance, LapsParser)

    assert "LapTimeRatio" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_lap_time_ratio, parser._processed_laps)


def test_compute_s2_lap_time(
    parser: LapsParser,
    processed_laps_after_compute_lap_time_ratio: DataFrame,
    processed_laps_after_compute_s2_lap_time: DataFrame,
) -> None:
    parser._processed_laps = processed_laps_after_compute_lap_time_ratio

    assert "S2LapTime" not in parser._processed_laps.columns

    instance = parser._compute_s2_lap_time()
    assert isinstance(instance, LapsParser)

    assert "S2LapTime" in parser._processed_laps.columns

    assert_frame_equal(processed_laps_after_compute_s2_lap_time, parser._processed_laps)


def test_parse(parser: LapsParser, laps: DataFrame, processed_laps: DataFrame) -> None:
    parser._laps = laps

    result = parser.parse()

    assert_frame_equal(processed_laps, result)
    assert_frame_equal(processed_laps, parser._processed_laps)


def test_parse_units(parser: LapsParser, mocker: MockerFixture) -> None:
    mock_atl = mocker.patch.object(parser, "_add_total_laps", return_value=parser)
    mock_csc = mocker.patch.object(parser, "_compute_sector_columns", return_value=parser)
    mock_clsttm = mocker.patch.object(parser, "_convert_lap_start_time_to_milliseconds", return_value=parser)
    mock_clttm = mocker.patch.object(parser, "_convert_lap_time_to_milliseconds", return_value=parser)
    mock_fltm = mocker.patch.object(parser, "_format_lap_time_milliseconds", return_value=parser)
    mock_cletm = mocker.patch.object(parser, "_compute_lap_end_time_milliseconds", return_value=parser)
    mock_cpittm = mocker.patch.object(parser, "_convert_pit_in_time_to_milliseconds", return_value=parser)
    mock_cpottm = mocker.patch.object(parser, "_convert_pit_out_time_to_milliseconds", return_value=parser)
    mock_alltm = mocker.patch.object(parser, "_add_last_lap_time_milliseconds", return_value=parser)
    mock_afltmsf = mocker.patch.object(parser, "_add_fastest_lap_time_milliseconds_so_far", return_value=parser)
    mock_fic = mocker.patch.object(parser, "_fill_in_compound", return_value=parser)
    mock_acc = mocker.patch.object(parser, "_add_compound_color", return_value=parser)
    mock_cltbm = mocker.patch.object(parser, "_compute_lap_time_best_milliseconds", return_value=parser)
    mock_cltpbm = mocker.patch.object(parser, "_compute_lap_time_personal_best_milliseconds", return_value=parser)
    mock_cltcc = mocker.patch.object(parser, "_compute_lap_time_color_code", return_value=parser)
    mock_cltc = mocker.patch.object(parser, "_compute_lap_time_color", return_value=parser)
    mock_cltr = mocker.patch.object(parser, "_compute_lap_time_ratio", return_value=parser)
    mock_cs2lt = mocker.patch.object(parser, "_compute_s2_lap_time", return_value=parser)

    parser.parse()

    mock_atl.assert_called_once()
    mock_csc.assert_has_calls([
        mocker.call(1),
        mocker.call(2),
        mocker.call(3),
    ])
    mock_clsttm.assert_called_once()
    mock_clttm.assert_called_once()
    mock_fltm.assert_called_once()
    mock_cletm.assert_called_once()
    mock_cpittm.assert_called_once()
    mock_cpottm.assert_called_once()
    mock_alltm.assert_called_once()
    mock_afltmsf.assert_called_once()
    mock_fic.assert_called_once()
    mock_acc.assert_called_once()
    mock_cltbm.assert_called_once()
    mock_cltpbm.assert_called_once()
    mock_cltcc.assert_called_once()
    mock_cltc.assert_called_once()
    mock_cltr.assert_called_once()
    mock_cs2lt.assert_called_once()


def test_slowest_non_pit_lap_property_fetches(parser: LapsParser, processed_laps: DataFrame, slowest_non_pit_lap: Series) -> None:
    assert parser._slowest_non_pit_lap is None

    parser._processed_laps = processed_laps

    assert_series_equal(slowest_non_pit_lap, parser.slowest_non_pit_lap)

    assert parser._slowest_non_pit_lap is not None
    assert_series_equal(slowest_non_pit_lap, parser._slowest_non_pit_lap)


def test_slowest_non_pit_lap_property_caches(parser: LapsParser, processed_laps: DataFrame, slowest_non_pit_lap: Series) -> None:
    assert parser._slowest_non_pit_lap is None

    parser._processed_laps = processed_laps

    assert_series_equal(slowest_non_pit_lap, parser.slowest_non_pit_lap), "First time computes"
    assert_series_equal(slowest_non_pit_lap, parser.slowest_non_pit_lap), "Second time caches"

    assert parser._slowest_non_pit_lap is not None


def test_slowest_non_pit_lap_property_returns_none_when_no_lap_matches_criteria(parser: LapsParser, processed_laps: DataFrame) -> None:
    assert parser._slowest_non_pit_lap is None

    df = processed_laps.copy()
    df.at[0, "TrackStatus"] = "12"
    df.at[3, "TrackStatus"] = "12"

    parser._processed_laps = df

    assert parser.slowest_non_pit_lap is None
    assert parser._slowest_non_pit_lap is None


def test_fastest_lap_property_fetches(parser: LapsParser, processed_laps: DataFrame, fastest_lap: Series) -> None:
    assert parser._slowest_non_pit_lap is None

    parser._processed_laps = processed_laps

    assert_series_equal(fastest_lap, parser.fastest_lap)

    assert parser._fastest_lap is not None
    assert_series_equal(fastest_lap, parser._fastest_lap)


def test_fastest_lap_property_caches(parser: LapsParser, processed_laps: DataFrame, fastest_lap: Series) -> None:
    assert parser._fastest_lap is None

    parser._processed_laps = processed_laps

    assert_series_equal(fastest_lap, parser.fastest_lap), "First time computes"
    assert_series_equal(fastest_lap, parser.fastest_lap), "Second time caches"

    assert parser._fastest_lap is not None


def test_fastest_lap_property_returns_none_when_no_lap_matches_criteria(parser: LapsParser, processed_laps: DataFrame) -> None:
    assert parser._fastest_lap is None

    df = processed_laps.copy()
    df["LapTimeMilliseconds"] = 0

    parser._processed_laps = df

    assert parser.fastest_lap is None
    assert parser._fastest_lap is None


def test_end_of_race_milliseconds_property_fetches(parser: LapsParser, processed_laps: DataFrame) -> None:
    assert parser._end_of_race_milliseconds is None

    parser._processed_laps = processed_laps

    assert 3691182 == parser.end_of_race_milliseconds

    assert parser._end_of_race_milliseconds is not None
    assert 3691182 == parser._end_of_race_milliseconds


def test_end_of_race_milliseconds_property_caches(parser: LapsParser, processed_laps: DataFrame, fastest_lap: Series) -> None:
    assert parser._end_of_race_milliseconds is None

    parser._processed_laps = processed_laps

    assert 3691182 == parser.end_of_race_milliseconds, "First time computes"
    assert 3691182 == parser.end_of_race_milliseconds, "Second time caches"

    assert parser._end_of_race_milliseconds is not None


def test_get_driver_laps(parser: LapsParser, processed_laps: DataFrame) -> None:
    assert parser._end_of_race_milliseconds is None

    parser._processed_laps = processed_laps

    driver_number = "24"

    expected = processed_laps[processed_laps["DriverNumber"] == driver_number].copy()

    assert_frame_equal(expected, parser.get_driver_laps(driver_number))


def test_get_driver_tire_strategy(parser: LapsParser, processed_laps: DataFrame) -> None:
    assert parser._end_of_race_milliseconds is None

    parser._processed_laps = processed_laps

    driver_number = "24"

    expected = {
        1.0: {'Compound': 'H', 'CompoundColor': (1, 1, 1, 0.8), 'LapNumber': 2.0, 'TotalLaps': 3},
        2.0: {'Compound': 'M', 'CompoundColor': (1, 1, 0, 0.8), 'LapNumber': 3.0, 'TotalLaps': 3},
    }

    assert expected == parser.get_driver_tire_strategy(driver_number)
