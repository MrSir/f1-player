from pathlib import Path
from unittest.mock import MagicMock, patch

import pandas as pd
import pytest
from fastf1.core import Lap, Laps, Session, Telemetry
from fastf1.events import Event, EventSchedule
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f
from pandas import DataFrame, Timedelta
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
    data_extractor_service: DataExtractorService, mocker: MockerFixture
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
    "session_tick,expected_lap",
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


def test_fastest_lap_fetches_and_caches(data_extractor_service: DataExtractorService, mocker: MockerFixture) -> None:
    mock_laps = mocker.MagicMock(spec=Laps)
    mock_fastest_lap = mocker.MagicMock(spec=Lap)
    mock_laps.pick_fastest.return_value = mock_fastest_lap
    data_extractor_service._laps = mock_laps

    result = data_extractor_service.fastest_lap

    assert result == mock_fastest_lap
    mock_laps.pick_fastest.assert_called_once()
    assert data_extractor_service._fastest_lap == mock_fastest_lap


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


def test_map_rotation(data_extractor_service: DataExtractorService, mock_circuit_info: MagicMock, mocker: MockerFixture) -> None:
    degs = 45.0
    radians = 0.7853981633974483

    mock_circuit_info.rotation = degs
    data_extractor_service._circuit_info = mock_circuit_info

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

