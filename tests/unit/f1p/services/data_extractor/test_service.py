from pathlib import Path
from unittest.mock import MagicMock

import numpy as np
import pandas as pd
import pytest
from fastf1.core import Lap, Laps, Session, Telemetry
from fastf1.events import Event, EventSchedule
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f
from pandas import DataFrame, Series, Timedelta
from pandas._testing import assert_frame_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.service import DataExtractorService


def test_init(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_text_font: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_accept = mocker.MagicMock()
    mock_enable_cache = mocker.MagicMock()
    mocker.patch.object(DataExtractorService, "accept", mock_accept)
    mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache", mock_enable_cache)
    mocker.patch.object(Path, "exists", return_value=True)

    service = DataExtractorService(
        parent=mock_parent,
        task_manager=mock_task_manager,
        window_width=1920,
        window_height=1080,
        text_font=mock_text_font,
    )

    assert service.parent == mock_parent
    assert service.task_manager == mock_task_manager
    assert service.window_width == 1920
    assert service.window_height == 1080
    assert service.text_font == mock_text_font

    assert service._event_schedule is None
    assert service._event is None
    assert service._session is None
    assert service._session_results is None
    assert service._session_status is None
    assert service._pos_data is None
    assert service._car_data is None
    assert service._total_laps is None

    mock_accept.assert_called_once_with("loadData", service.load_data)
    mock_enable_cache.assert_called_once()


def test_init_and_create_cache_dir(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_text_font: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_accept = mocker.MagicMock()
    mock_enable_cache = mocker.MagicMock()
    mocker.patch.object(DataExtractorService, "accept", mock_accept)
    mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache", mock_enable_cache)
    mocker.patch.object(Path, "exists", return_value=True)

    mock_path = mocker.MagicMock(spec=Path)
    mock_path.exists.return_value = False
    DataExtractorService.cache_path = mock_path

    service = DataExtractorService(
        parent=mock_parent,
        task_manager=mock_task_manager,
        window_width=1920,
        window_height=1080,
        text_font=mock_text_font,
    )

    assert service.parent == mock_parent
    assert service.task_manager == mock_task_manager
    assert service.window_width == 1920
    assert service.window_height == 1080
    assert service.text_font == mock_text_font

    assert service._event_schedule is None
    assert service._event is None
    assert service._session is None
    assert service._session_results is None
    assert service._session_status is None
    assert service._pos_data is None
    assert service._car_data is None
    assert service._total_laps is None

    mock_accept.assert_called_once_with("loadData", service.load_data)
    mock_enable_cache.assert_called_once()

    mock_path.exists.assert_called_once()
    mock_path.mkdir.assert_called_once_with(parents=True)


def test_event_schedule_returns_cached_value(
    data_extractor_service: DataExtractorService,
    mocker: MockerFixture,
) -> None:
    mock_event_schedule = mocker.MagicMock(spec=EventSchedule)
    data_extractor_service._event_schedule = mock_event_schedule

    result = data_extractor_service.event_schedule

    assert result == mock_event_schedule


def test_event_schedule_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_event_schedule = mocker.MagicMock(spec=EventSchedule)
    mock_get_event_schedule = mocker.patch(
        "f1p.services.data_extractor.service.fastf1.get_event_schedule",
        return_value=mock_event_schedule,
    )

    result = data_extractor_service.event_schedule

    assert result == mock_event_schedule
    mock_get_event_schedule.assert_called_once_with(2024)
    assert data_extractor_service._event_schedule == mock_event_schedule


def test_event_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_event = mocker.MagicMock(spec=Event)
    data_extractor_service._event = mock_event

    result = data_extractor_service.event

    assert result == mock_event


def test_event_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_event = mocker.MagicMock(spec=Event)
    mock_get_event = mocker.patch(
        "f1p.services.data_extractor.service.fastf1.get_event",
        return_value=mock_event,
    )

    result = data_extractor_service.event

    assert result == mock_event
    mock_get_event.assert_called_once_with(2024, "Bahrain")
    assert data_extractor_service._event == mock_event


def test_session_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    data_extractor_service._session = mock_session

    result = data_extractor_service.session

    assert result == mock_session


def test_session_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_get_session = mocker.patch(
        "f1p.services.data_extractor.service.fastf1.get_session",
        return_value=mock_session,
    )

    result = data_extractor_service.session

    assert result == mock_session
    mock_get_session.assert_called_once_with(2024, "Bahrain", "FP1")
    assert data_extractor_service._session == mock_session


def test_session_results_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_results = pd.DataFrame({"Driver": ["VER", "LEC"]})
    data_extractor_service._session_results = mock_results

    result = data_extractor_service.session_results

    assert result.equals(mock_results)


def test_session_results_raises_when_not_loaded(data_extractor_service: DataExtractorService) -> None:
    with pytest.raises(ValueError, match="Session results are not loaded yet."):
        data_extractor_service.session_results


def test_session_status_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_status = pd.DataFrame({"Status": [1, 2]})
    data_extractor_service._session_status = mock_status

    result = data_extractor_service.session_status

    assert result.equals(mock_status)


def test_session_status_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_status = pd.DataFrame({"Status": [1, 2]})
    mock_session.session_status = mock_status
    data_extractor_service._session = mock_session

    result = data_extractor_service.session_status

    assert result.equals(mock_status)
    assert data_extractor_service._session_status is not None


def test_total_laps_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    data_extractor_service._total_laps = 50

    result = data_extractor_service.total_laps

    assert result == 50


def test_total_laps_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_session.total_laps = 50
    data_extractor_service._session = mock_session

    result = data_extractor_service.total_laps

    assert result == 50
    assert data_extractor_service._total_laps == 50


def test_pos_data_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_pos_data = {"VER": mocker.MagicMock(spec=Telemetry)}
    data_extractor_service._pos_data = mock_pos_data

    result = data_extractor_service.pos_data

    assert result == mock_pos_data


def test_pos_data_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_pos_data = {"VER": mocker.MagicMock(spec=Telemetry), "LEC": mocker.MagicMock(spec=Telemetry)}
    mock_session.pos_data = mock_pos_data
    data_extractor_service._session = mock_session

    result = data_extractor_service.pos_data

    assert result == mock_pos_data
    assert data_extractor_service._pos_data == mock_pos_data


def test_car_data_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_car_data = {"VER": mocker.MagicMock(spec=Telemetry)}
    data_extractor_service._car_data = mock_car_data

    result = data_extractor_service.car_data

    assert result == mock_car_data


def test_car_data_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_car_data = {"VER": mocker.MagicMock(spec=Telemetry), "LEC": mocker.MagicMock(spec=Telemetry)}
    mock_session.car_data = mock_car_data
    data_extractor_service._session = mock_session

    result = data_extractor_service.car_data

    assert result == mock_car_data
    assert data_extractor_service._car_data == mock_car_data


def test_laps_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_laps = mocker.MagicMock(spec=Laps)
    data_extractor_service._laps = mock_laps

    result = data_extractor_service.laps

    assert result == mock_laps


def test_laps_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_laps = mocker.MagicMock(spec=Laps)
    mock_session.laps = mock_laps
    data_extractor_service._session = mock_session

    result = data_extractor_service.laps

    assert result == mock_laps
    assert data_extractor_service._laps == mock_laps


@pytest.mark.parametrize(
    ("session_tick", "expected_lap"),
    [
        (1, 1),
        (2, 2),
        (3, 3),
    ],
)
def test_get_current_lap_number_parametrized(
    data_extractor_service: DataExtractorService,
    session_tick: int,
    expected_lap: int,
) -> None:
    mock_pos_data = pd.DataFrame({
        "SessionTimeTick": [1, 2, 3],
        "LapsCompletion": [0.5, 1.5, 2.5],
    })
    data_extractor_service.processed_pos_data = mock_pos_data

    result = data_extractor_service.get_current_lap_number(session_tick)

    assert result == expected_lap


def test_fastest_lap_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_lap = mocker.MagicMock(spec=Lap)
    data_extractor_service._fastest_lap = mock_lap

    result = data_extractor_service.fastest_lap

    assert result == mock_lap


def test_fastest_lap_fetches_and_caches(
    data_extractor_service: DataExtractorService,
    laps_df: DataFrame,
    fastest_lap: Series,
) -> None:
    data_extractor_service._laps = laps_df
    result = data_extractor_service.fastest_lap

    assert fastest_lap.equals(result)
    assert fastest_lap.equals(data_extractor_service._fastest_lap)


def test_lowest_z_coordinate(data_extractor_service: DataExtractorService) -> None:
    mock_pos_data = pd.DataFrame({
        "Z": [5.0, 2.0, 8.0, 1.0, 3.0],
    })
    data_extractor_service.processed_pos_data = mock_pos_data

    result = data_extractor_service.lowest_z_coordinate

    assert result == 1.0


def test_lowest_z_coordinate_with_negative_values(data_extractor_service: DataExtractorService) -> None:
    mock_pos_data = pd.DataFrame({
        "Z": [5.0, -2.0, 8.0, -5.0, 3.0],
    })
    data_extractor_service.processed_pos_data = mock_pos_data

    result = data_extractor_service.lowest_z_coordinate

    assert result == -5.0


def test_circuit_info_returns_cached_value(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_circuit_info = mocker.MagicMock(spec=CircuitInfo)
    data_extractor_service._circuit_info = mock_circuit_info

    result = data_extractor_service.circuit_info

    assert result == mock_circuit_info


def test_circuit_info_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_circuit_info = mocker.MagicMock(spec=CircuitInfo)
    mock_session.get_circuit_info.return_value = mock_circuit_info
    data_extractor_service._session = mock_session

    result = data_extractor_service.circuit_info

    assert result == mock_circuit_info
    mock_session.get_circuit_info.assert_called_once()
    assert data_extractor_service._circuit_info == mock_circuit_info


def test_processed_corners_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_corners = pd.DataFrame({"X": [1, 2], "Y": [3, 4]})
    data_extractor_service._processed_corners = mock_corners

    result = data_extractor_service.processed_corners

    assert result.equals(mock_corners)


def test_processed_corners_raises_when_not_processed(data_extractor_service: DataExtractorService) -> None:
    with pytest.raises(ValueError, match="Corners are not processed yet."):
        data_extractor_service.processed_corners


def test_track_status_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_track_status = pd.DataFrame({"Status": [1, 2]})
    data_extractor_service._track_status = mock_track_status

    result = data_extractor_service.track_status

    assert result.equals(mock_track_status)


def test_track_status_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_track_status = pd.DataFrame({"Status": [1, 2]})
    mock_session.track_status = mock_track_status
    data_extractor_service._session = mock_session

    result = data_extractor_service.track_status

    assert result.equals(mock_track_status)
    assert data_extractor_service._track_status is not None


def test_track_status_colors_creates_dataframe(
    data_extractor_service: DataExtractorService,
    track_status_colors: DataFrame,
) -> None:
    data_extractor_service._track_status_colors = None
    result = data_extractor_service.track_status_colors

    assert result.equals(track_status_colors)


def test_green_flag_track_status_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_green_flag_status = pd.DataFrame({
        "Status": [1],
        "Label": ["Green Flag"],
    })
    data_extractor_service._green_flag_track_status = mock_green_flag_status

    result = data_extractor_service.green_flag_track_status

    assert result.equals(mock_green_flag_status)


def test_green_flag_track_status_filters_status_one(data_extractor_service: DataExtractorService) -> None:
    result = data_extractor_service.green_flag_track_status

    assert len(result) == 1
    assert result["Status"].iloc[0] == 1
    assert data_extractor_service._green_flag_track_status is not None


def test_green_flag_track_status_label(data_extractor_service: DataExtractorService) -> None:
    result = data_extractor_service.green_flag_track_status_label

    assert result == "Green Flag"


def test_green_flag_track_status_color(data_extractor_service: DataExtractorService) -> None:
    result = data_extractor_service.green_flag_track_status_color

    assert result == LVecBase4f(0, 1, 0, 0.8)


def test_green_flag_track_status_text_color(data_extractor_service: DataExtractorService) -> None:
    result = data_extractor_service.green_flag_track_status_text_color

    assert result == LVecBase4f(0, 0, 0, 0.8)


def test_weather_data_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_weather = pd.DataFrame({"Temp": [20, 21]})
    data_extractor_service._weather_data = mock_weather

    result = data_extractor_service.weather_data

    assert result.equals(mock_weather)


def test_weather_data_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_session = mocker.MagicMock(spec=Session)
    mock_weather = pd.DataFrame({"Temp": [20, 21]})
    mock_session.weather_data = mock_weather
    data_extractor_service._session = mock_session

    result = data_extractor_service.weather_data

    assert result.equals(mock_weather)
    assert data_extractor_service._weather_data is not None


def test_map_rotation(
    data_extractor_service: DataExtractorService,
        circuit_info: MagicMock,
    mocker: MockerFixture,
) -> None:
    degs = 45.0
    radians = 0.7853981633974483

    circuit_info.rotation = degs
    data_extractor_service._circuit_info = circuit_info

    mock_deg2rad = mocker.patch("f1p.services.data_extractor.service.deg2Rad", return_value=radians)

    result = data_extractor_service.map_rotation

    mock_deg2rad.assert_called_once_with(degs)
    assert result == radians


def test_session_start_time_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_start_time = Timedelta(milliseconds=1000)
    data_extractor_service._session_start_time = mock_start_time

    result = data_extractor_service.session_start_time

    assert result == mock_start_time


def test_session_start_time_fetches_and_caches(
    data_extractor_service: DataExtractorService,
    mock_session_status: DataFrame,
) -> None:
    data_extractor_service._session_status = mock_session_status

    result = data_extractor_service.session_start_time

    assert result == Timedelta(milliseconds=1000)
    assert data_extractor_service._session_start_time is not None


def test_session_start_time_milliseconds(
    data_extractor_service: DataExtractorService,
    mock_session_status: DataFrame,
) -> None:
    data_extractor_service._session_status = mock_session_status

    result = data_extractor_service.session_start_time_milliseconds

    assert result == 1000


def test_session_start_time_milliseconds_with_larger_value(
    data_extractor_service: DataExtractorService,
) -> None:
    mock_status = pd.DataFrame({
        "Status": ["Started"],
        "Time": [Timedelta(seconds=5)],
    })
    data_extractor_service._session_status = mock_status

    result = data_extractor_service.session_start_time_milliseconds

    assert result == 5000


def test_session_end_time_returns_cached_value(data_extractor_service: DataExtractorService) -> None:
    mock_end_time = Timedelta(milliseconds=5000)
    data_extractor_service._session_end_time = mock_end_time

    result = data_extractor_service.session_end_time

    assert result == mock_end_time


def test_session_end_time_fetches_and_caches(
    data_extractor_service: DataExtractorService,
    mock_session_status: DataFrame,
) -> None:
    data_extractor_service._session_status = mock_session_status

    result = data_extractor_service.session_end_time

    assert result == Timedelta(milliseconds=5000)
    assert data_extractor_service._session_end_time is not None


def test_session_end_time_milliseconds(
    data_extractor_service: DataExtractorService,
    mock_session_status: DataFrame,
) -> None:
    data_extractor_service._session_status = mock_session_status

    result = data_extractor_service.session_end_time_milliseconds

    assert result == 5000


def test_session_ticks(data_extractor_service: DataExtractorService) -> None:
    mock_pos_data = pd.DataFrame({
        "DriverNumber": [1, 1, 1, 2, 2, 3],
        "SessionTimeTick": [1, 2, 3, 1, 2, 1],
    })
    data_extractor_service.processed_pos_data = mock_pos_data

    result = data_extractor_service.session_ticks

    assert result == 1


def test_session_ticks_with_different_driver_counts(data_extractor_service: DataExtractorService) -> None:
    mock_pos_data = pd.DataFrame({
        "DriverNumber": [1, 1, 1, 1, 2, 2, 3],
        "SessionTimeTick": [1, 2, 3, 4, 1, 2, 1],
    })
    data_extractor_service.processed_pos_data = mock_pos_data

    result = data_extractor_service.session_ticks

    assert result == 1


def test_process_track_statuses(
    data_extractor_service: DataExtractorService,
    mock_pos_data_with_session_time: DataFrame,
    processed_track_statuses: DataFrame,
    track_status_colors: DataFrame,
    mocker: MockerFixture,
) -> None:
    data_extractor_service.processed_pos_data = mock_pos_data_with_session_time
    data_extractor_service._session_start_time = Timedelta(milliseconds=1000)
    data_extractor_service._session_end_time = Timedelta(milliseconds=5000)

    mock_track_status_df = pd.DataFrame({
        "Status": [1, 2],
        "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000)],
    })
    data_extractor_service._track_status = mock_track_status_df
    data_extractor_service._track_status_colors = track_status_colors
    mocker.patch.object(data_extractor_service, "update_loading")

    data_extractor_service.process_track_statuses(500)
    assert_frame_equal(processed_track_statuses, data_extractor_service._track_statuses)


def test_track_statuses_returns_cached_value(
    data_extractor_service: DataExtractorService,
    processed_track_statuses: DataFrame,
) -> None:
    data_extractor_service._track_statuses = processed_track_statuses

    result = data_extractor_service.track_statuses

    assert result.equals(processed_track_statuses)


def test_track_statuses_raises_when_not_processed(data_extractor_service: DataExtractorService) -> None:
    with pytest.raises(ValueError, match="Track statuses not processed."):
        data_extractor_service.track_statuses


def test_get_current_track_status_returns_matching_status(
    data_extractor_service: DataExtractorService,
    processed_track_statuses: DataFrame,
) -> None:
    data_extractor_service._track_statuses = processed_track_statuses

    result = data_extractor_service.get_current_track_status(2)

    assert result is not None
    assert result["Status"] == np.int64(1)


def test_get_current_track_status_returns_none_when_not_found(
    data_extractor_service: DataExtractorService,
    processed_track_statuses: DataFrame,
) -> None:
    data_extractor_service._track_statuses = processed_track_statuses

    result = data_extractor_service.get_current_track_status(100)

    assert result is None


@pytest.mark.parametrize(
    ("session_time_tick", "expected_status"),
    [
        (1, 1),
        (2, 1),
        (4, 2),
    ],
)
def test_get_current_track_status_parametrized(
    data_extractor_service: DataExtractorService,
    processed_track_statuses: DataFrame,
    session_time_tick: int,
    expected_status: int,
) -> None:
    data_extractor_service._track_statuses = processed_track_statuses

    result = data_extractor_service.get_current_track_status(session_time_tick)

    assert result is not None
    assert result["Status"] == expected_status


def test_get_current_weather_data_returns_matching_data(
    data_extractor_service: DataExtractorService,
    processed_weather_data: DataFrame,
) -> None:
    data_extractor_service.processed_weather_data = processed_weather_data

    result = data_extractor_service.get_current_weather_data(3)

    assert result is not None
    assert result["SessionTimeTick"] == 3


def test_get_current_weather_data_returns_none_when_not_found(
    data_extractor_service: DataExtractorService,
    processed_weather_data: DataFrame,
) -> None:
    data_extractor_service.processed_weather_data = processed_weather_data

    result = data_extractor_service.get_current_weather_data(0)

    assert result is None


@pytest.mark.parametrize(
    ("session_time_tick", "expected_tick"),
    [
        (1, 1),
        (3, 3),
        (5, 5),
    ],
)
def test_get_current_weather_data_parametrized(
    data_extractor_service: DataExtractorService,
    processed_weather_data: DataFrame,
    session_time_tick: int,
    expected_tick: int,
) -> None:
    data_extractor_service.processed_weather_data = processed_weather_data

    result = data_extractor_service.get_current_weather_data(session_time_tick)

    assert result is not None
    assert result["SessionTimeTick"] == expected_tick


def test_process_fastest_lap(
    data_extractor_service: DataExtractorService,
    fastest_lap_data: DataFrame,
    mocker: MockerFixture,
) -> None:
    mock_fastest_lap = mocker.MagicMock(spec=Lap)
    mock_fastest_lap.get_pos_data.return_value = fastest_lap_data
    data_extractor_service._fastest_lap = mock_fastest_lap

    mock_resize = mocker.patch("f1p.services.data_extractor.service.resize_pos_data", return_value=fastest_lap_data)
    mock_find_center = mocker.patch("f1p.services.data_extractor.service.find_center", return_value=(2.0, 2.0, 0.0))
    mock_center = mocker.patch("f1p.services.data_extractor.service.center_pos_data", return_value=fastest_lap_data)
    mocker.patch(
        "f1p.services.data_extractor.service.DataExtractorService.map_rotation",
        new_callable=mocker.PropertyMock,
        return_value=0.785,
    )
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.process_fastest_lap()

    assert result == data_extractor_service
    assert data_extractor_service.map_center_coordinate == (2.0, 2.0, 0.0)
    assert data_extractor_service.fastest_lap_telemetry is not None
    mock_resize.assert_called_once()
    mock_find_center.assert_called_once()
    mock_center.assert_called_once()
    mock_update_loading.assert_called_once_with(1)


def test_combine_position_data(
    data_extractor_service: DataExtractorService,
    fastest_lap_data: DataFrame,
    mocker: MockerFixture,
) -> None:
    mock_pos_data = {
        "1": fastest_lap_data.copy(),
        "2": fastest_lap_data.copy(),
    }
    data_extractor_service._pos_data = mock_pos_data
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.combine_position_data()

    assert result == data_extractor_service
    assert data_extractor_service.processed_pos_data is not None
    assert len(data_extractor_service.processed_pos_data) == 8
    assert "DriverNumber" in data_extractor_service.processed_pos_data.columns
    mock_update_loading.assert_called_once_with(2)

    driver_numbers = data_extractor_service.processed_pos_data["DriverNumber"].unique()
    assert len(driver_numbers) == 2
    assert "1" in driver_numbers
    assert "2" in driver_numbers


def test_remove_records_before_session_start_time(
    data_extractor_service: DataExtractorService,
    pos_data_for_filtering: DataFrame,
    mocker: MockerFixture,
) -> None:
    data_extractor_service.processed_pos_data = pos_data_for_filtering.copy()
    data_extractor_service._session_start_time = Timedelta(milliseconds=1000)
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.remove_records_before_session_start_time()

    assert result == data_extractor_service
    assert len(data_extractor_service.processed_pos_data) == 4
    assert data_extractor_service.processed_pos_data["SessionTime"].min() == Timedelta(milliseconds=1000)
    mock_update_loading.assert_called_once_with(1)


def test_normalize_position_data(
    data_extractor_service: DataExtractorService,
    pos_data_for_normalization: DataFrame,
    mocker: MockerFixture,
) -> None:
    data_extractor_service.processed_pos_data = pos_data_for_normalization.copy()
    data_extractor_service.map_center_coordinate = (2.0, 2.0, 0.0)

    mock_resize = mocker.patch(
        "f1p.services.data_extractor.service.resize_pos_data",
        return_value=pos_data_for_normalization,
    )
    mock_center = mocker.patch(
        "f1p.services.data_extractor.service.center_pos_data",
        return_value=pos_data_for_normalization,
    )
    mocker.patch(
        "f1p.services.data_extractor.service.DataExtractorService.map_rotation",
        new_callable=mocker.PropertyMock,
        return_value=0.785,
    )
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.normalize_position_data()

    assert result == data_extractor_service
    assert data_extractor_service.processed_pos_data is not None
    mock_resize.assert_called_once()
    mock_center.assert_called_once()
    mock_update_loading.assert_called_once_with(5)


def test_add_session_time_in_milliseconds(
    data_extractor_service: DataExtractorService,
    pos_data_for_milliseconds: DataFrame,
    mocker: MockerFixture,
) -> None:
    data_extractor_service.processed_pos_data = pos_data_for_milliseconds.copy()
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.add_session_time_in_milliseconds()

    assert result == data_extractor_service
    assert "SessionTimeMilliseconds" in data_extractor_service.processed_pos_data.columns
    assert data_extractor_service.processed_pos_data["SessionTimeMilliseconds"].dtype == "int64"
    assert data_extractor_service.processed_pos_data["SessionTimeMilliseconds"].tolist() == [1000, 2000, 3000]
    mock_update_loading.assert_called_once_with(1)


def test_add_session_time_tick(
    data_extractor_service: DataExtractorService,
    pos_data_for_session_time_tick: DataFrame,
    mocker: MockerFixture,
) -> None:
    data_extractor_service.processed_pos_data = pos_data_for_session_time_tick.copy()
    mock_update_loading = mocker.patch.object(data_extractor_service, "update_loading")

    result = data_extractor_service.add_session_time_tick()

    assert result == data_extractor_service
    assert "SessionTimeTick" in data_extractor_service.processed_pos_data.columns

    driver_1_ticks = data_extractor_service.processed_pos_data[
        data_extractor_service.processed_pos_data["DriverNumber"] == 1
    ]["SessionTimeTick"].tolist()
    driver_2_ticks = data_extractor_service.processed_pos_data[
        data_extractor_service.processed_pos_data["DriverNumber"] == 2
    ]["SessionTimeTick"].tolist()

    assert driver_1_ticks == [1, 2, 3]
    assert driver_2_ticks == [1, 2, 3]
    mock_update_loading.assert_called_once_with(1)
