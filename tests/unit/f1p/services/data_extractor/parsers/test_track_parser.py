from unittest.mock import MagicMock

import pytest
from fastf1.mvapi import CircuitInfo
from panda3d.core import deg2Rad
from pandas import DataFrame, Timedelta
from pandas._testing import assert_frame_equal, assert_series_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.parsers.track import TrackParser
from f1p.services.data_extractor.track_statuses import GreenFlagTrackStatus


@pytest.fixture()
def parser(mock_session: MagicMock) -> TrackParser:
    return TrackParser(mock_session)


def test_initialization(mock_session: MagicMock) -> None:
    parser = TrackParser(mock_session)

    assert mock_session == parser.session
    assert parser._circuit_info is None
    assert parser._corners is None
    assert parser._track_status is None
    assert parser._track_status_colors is None
    assert parser._green_flag_track_status is None

    assert parser._augmented_session_time_ticks_df is None
    assert parser._processed_track_statuses is None


def test_circuit_info_property_fetches(parser: TrackParser, mock_session: MagicMock, circuit_info: CircuitInfo) -> None:
    assert parser._circuit_info is None

    assert circuit_info == parser.circuit_info
    assert circuit_info == parser._circuit_info

    mock_session.get_circuit_info.assert_called_once()


def test_circuit_info_property_caches(parser: TrackParser, mock_session: MagicMock, circuit_info: CircuitInfo) -> None:
    assert parser._circuit_info is None

    assert circuit_info == parser.circuit_info, "First time computes"
    assert circuit_info == parser.circuit_info, "Second time caches"

    mock_session.get_circuit_info.assert_called_once()


def test_map_rotation_property(parser: TrackParser, circuit_info: MagicMock) -> None:
    parser._circuit_info = circuit_info

    assert deg2Rad(circuit_info.rotation) == parser.map_rotation


def test_corners_property_fetches(parser: TrackParser, circuit_info: CircuitInfo) -> None:
    parser._circuit_info = circuit_info
    assert parser._corners is None

    assert circuit_info.corners.equals(parser.corners)
    assert parser._corners is not None
    assert circuit_info.corners.equals(parser._corners)


def test_corners_property_caches(parser: TrackParser, circuit_info: CircuitInfo) -> None:
    parser._circuit_info = circuit_info
    assert parser._corners is None

    assert circuit_info.corners.equals(parser.corners), "First time computes"
    assert circuit_info.corners.equals(parser.corners), "Second time caches"


def test_track_status_property_fetches(parser: TrackParser, track_status: DataFrame) -> None:
    assert parser._track_status is None

    assert track_status.equals(parser.track_status)
    assert parser._track_status is not None
    assert track_status.equals(parser._track_status)


def test_track_status_property_caches(parser: TrackParser, track_status: DataFrame) -> None:
    assert parser._track_status is None

    assert track_status.equals(parser.track_status), "First time computes"
    assert track_status.equals(parser.track_status), "Second time caches"


def test_track_status_colors_property_fetches(parser: TrackParser, track_status_colors: DataFrame) -> None:
    assert parser._track_status_colors is None

    assert_frame_equal(track_status_colors, parser.track_status_colors)
    assert parser._track_status_colors is not None
    assert_frame_equal(track_status_colors, parser._track_status_colors)


def test_track_status_colors_property_caches(parser: TrackParser, track_status_colors: DataFrame) -> None:
    assert parser._track_status_colors is None

    assert_frame_equal(track_status_colors, parser.track_status_colors), "First time computes"
    assert_frame_equal(track_status_colors, parser.track_status_colors), "Second time caches"


def test_green_flag_track_status_property_fetches(parser: TrackParser) -> None:
    assert parser._green_flag_track_status is None

    green_flag_track_status = GreenFlagTrackStatus()

    assert_series_equal(green_flag_track_status, parser.green_flag_track_status)
    assert parser._green_flag_track_status is not None
    assert_series_equal(green_flag_track_status, parser._green_flag_track_status)


def test_green_flag_track_status_property_caches(parser: TrackParser) -> None:
    assert parser._green_flag_track_status is None

    green_flag_track_status = GreenFlagTrackStatus()

    assert_series_equal(green_flag_track_status, parser.green_flag_track_status), "First time computes"
    assert_series_equal(green_flag_track_status, parser.green_flag_track_status), "Second time caches"


def test_process_corners(parser: TrackParser, circuit_info: CircuitInfo, processed_corners: DataFrame) -> None:
    parser._circuit_info = circuit_info

    map_center_coordinate = (1.2, 1.3, 1.4)

    assert_frame_equal(processed_corners, parser.process_corners(map_center_coordinate))


def test_augment_session_time_ticks(
    parser: TrackParser,
    session_time_ticks_df: DataFrame,
    augmented_session_time_ticks_df: DataFrame,
) -> None:
    width = 100
    session_ticks = 5

    instance = parser._augment_session_time_ticks(width, session_ticks, session_time_ticks_df)

    assert isinstance(instance, TrackParser)
    assert_frame_equal(augmented_session_time_ticks_df, parser._augmented_session_time_ticks_df)


def test_trim_to_session_time(
    parser: TrackParser,
    circuit_info: CircuitInfo,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_track_statuses_after_trim_to_session_time: DataFrame,
) -> None:
    parser._circuit_info = circuit_info

    assert parser._processed_track_statuses is None

    instance = parser._trim_to_session_time(session_start_time, session_end_time)

    assert isinstance(instance, TrackParser)
    assert parser._processed_track_statuses is not None

    assert_frame_equal(processed_track_statuses_after_trim_to_session_time, parser._processed_track_statuses)


def test_add_session_time_ticks(
    parser: TrackParser,
    processed_track_statuses_after_trim_to_session_time: DataFrame,
    augmented_session_time_ticks_df: DataFrame,
    processed_track_statuses_after_add_session_time_ticks: DataFrame,
) -> None:
    parser._processed_track_statuses = processed_track_statuses_after_trim_to_session_time
    parser._augmented_session_time_ticks_df = augmented_session_time_ticks_df

    assert "SessionTimeTick" not in parser._processed_track_statuses.columns
    assert "SessionTimeTickEnd" not in parser._processed_track_statuses.columns

    instance = parser._add_session_time_ticks()

    assert isinstance(instance, TrackParser)
    assert "SessionTimeTick" in parser._processed_track_statuses.columns
    assert "SessionTimeTickEnd" in parser._processed_track_statuses.columns

    assert_frame_equal(processed_track_statuses_after_add_session_time_ticks, parser._processed_track_statuses)


def test_merge_in_augmented_session_time_ticks(
    parser: TrackParser,
    processed_track_statuses_after_add_session_time_ticks: DataFrame,
    augmented_session_time_ticks_df: DataFrame,
    processed_track_statuses_after_merge_augmented_session_time_ticks: DataFrame,
) -> None:
    parser._processed_track_statuses = processed_track_statuses_after_add_session_time_ticks
    parser._augmented_session_time_ticks_df = augmented_session_time_ticks_df

    assert "PixelStart" not in parser._processed_track_statuses.columns
    assert "PixelEnd" not in parser._processed_track_statuses.columns

    instance = parser._merge_in_augmented_session_time_ticks()

    assert isinstance(instance, TrackParser)

    assert "PixelStart" in parser._processed_track_statuses.columns
    assert "PixelEnd" in parser._processed_track_statuses.columns
    assert "SessionTime" not in parser._processed_track_statuses.columns
    assert "SessionTimeTick_y" not in parser._processed_track_statuses.columns
    assert "Time" not in parser._processed_track_statuses.columns
    assert "EndTime" not in parser._processed_track_statuses.columns

    assert_frame_equal(
        processed_track_statuses_after_merge_augmented_session_time_ticks, parser._processed_track_statuses,
    )


def test_compute_width(
    parser: TrackParser,
    processed_track_statuses_after_merge_augmented_session_time_ticks: DataFrame,
    processed_track_statuses_after_compute_width: DataFrame,
) -> None:
    parser._processed_track_statuses = processed_track_statuses_after_merge_augmented_session_time_ticks

    assert "Width" not in parser._processed_track_statuses.columns

    instance = parser._compute_width()

    assert isinstance(instance, TrackParser)

    assert "Width" in parser._processed_track_statuses.columns

    assert_frame_equal(processed_track_statuses_after_compute_width, parser._processed_track_statuses)


def test_convert_status_to_integer(
    parser: TrackParser,
    processed_track_statuses_after_compute_width: DataFrame,
    processed_track_statuses_after_convert_status_to_int: DataFrame,
) -> None:
    parser._processed_track_statuses = processed_track_statuses_after_compute_width

    assert parser._processed_track_statuses["Status"].dtype == object

    instance = parser._convert_status_to_integer()

    assert isinstance(instance, TrackParser)

    assert parser._processed_track_statuses["Status"].dtype == "int64"

    assert_frame_equal(processed_track_statuses_after_convert_status_to_int, parser._processed_track_statuses)


def test_merge_status_colors(
    parser: TrackParser,
    processed_track_statuses_after_convert_status_to_int: DataFrame,
    processed_track_statuses: DataFrame,
) -> None:
    parser._processed_track_statuses = processed_track_statuses_after_convert_status_to_int

    assert "Label" not in parser._processed_track_statuses.columns
    assert "Color" not in parser._processed_track_statuses.columns
    assert "TextColor" not in parser._processed_track_statuses.columns

    instance = parser._merge_status_colors()

    assert isinstance(instance, TrackParser)

    assert "Label" in parser._processed_track_statuses.columns
    assert "Color" in parser._processed_track_statuses.columns
    assert "TextColor" in parser._processed_track_statuses.columns

    assert_frame_equal(processed_track_statuses, parser._processed_track_statuses)


def test_process_track_statuses(
    parser: TrackParser,
    circuit_info: CircuitInfo,
    session_time_ticks_df: DataFrame,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_track_statuses: DataFrame,
) -> None:
    parser._circuit_info = circuit_info

    result_df = parser.process_track_statuses(100, 5, session_time_ticks_df, session_start_time, session_end_time)

    assert_frame_equal(processed_track_statuses, parser._processed_track_statuses)
    assert_frame_equal(processed_track_statuses, result_df)


def test_process_track_statuses_units(
    parser: TrackParser,
    circuit_info: CircuitInfo,
    session_time_ticks_df: DataFrame,
    session_start_time: Timedelta,
    session_end_time: Timedelta,
    processed_track_statuses: DataFrame,
    mocker: MockerFixture,
) -> None:
    parser._circuit_info = circuit_info
    parser._processed_track_statuses = processed_track_statuses

    width = 100
    session_ticks = 5

    mock_augment_stt = mocker.patch.object(parser, "_augment_session_time_ticks", return_value=parser)
    mock_ttst = mocker.patch.object(parser, "_trim_to_session_time", return_value=parser)
    mock_add_stt = mocker.patch.object(parser, "_add_session_time_ticks", return_value=parser)
    mock_miastt = mocker.patch.object(parser, "_merge_in_augmented_session_time_ticks", return_value=parser)
    mock_cw = mocker.patch.object(parser, "_compute_width", return_value=parser)
    mock_csti = mocker.patch.object(parser, "_convert_status_to_integer", return_value=parser)
    mock_msc = mocker.patch.object(parser, "_merge_status_colors", return_value=parser)

    result_df = parser.process_track_statuses(
        width, session_ticks, session_time_ticks_df, session_start_time, session_end_time,
    )

    assert_frame_equal(processed_track_statuses, parser._processed_track_statuses)
    assert_frame_equal(processed_track_statuses, result_df)

    mock_augment_stt.assert_called_once_with(width, session_ticks, session_time_ticks_df)
    mock_ttst.assert_called_once_with(session_start_time, session_end_time)
    mock_add_stt.assert_called_once()
    mock_miastt.assert_called_once()
    mock_cw.assert_called_once()
    mock_csti.assert_called_once()
    mock_msc.assert_called_once()
