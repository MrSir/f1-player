from unittest.mock import MagicMock

import pandas as pd
import pytest
from direct.task.Task import TaskManager
from fastf1.core import Telemetry
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f, NodePath, StaticTextFont
from pandas import DataFrame, Timedelta
from pytest_mock import MockerFixture

from f1p.services.data_extractor.service import DataExtractorService


@pytest.fixture()
def mock_parent(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=NodePath)


@pytest.fixture()
def mock_task_manager(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=TaskManager)


@pytest.fixture()
def mock_text_font(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=StaticTextFont)


@pytest.fixture()
def data_extractor_service(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_text_font: MagicMock,
    mocker: MockerFixture,
) -> DataExtractorService:
    mocker.patch.object(DataExtractorService, "accept")
    mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache")

    service = DataExtractorService(
        parent=mock_parent,
        task_manager=mock_task_manager,
        window_width=1920,
        window_height=1080,
        text_font=mock_text_font,
    )
    service.year = 2024
    service.event_name = "Bahrain"
    service.session_id = "FP1"

    return service


@pytest.fixture()
def mock_session_status() -> DataFrame:
    return pd.DataFrame({
        "Status": ["Started", "Finalised"],
        "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=5000)],
    })


@pytest.fixture()
def mock_processed_pos_data() -> DataFrame:
    return pd.DataFrame({
        "SessionTimeTick": [1, 2, 3, 4, 5],
        "LapsCompletion": [0.5, 1.2, 1.8, 2.1, 2.9],
        "Z": [0.0, 1.5, 2.0, 1.8, 0.5],
        "DriverNumber": [1, 1, 2, 2, 1],
    })


@pytest.fixture()
def mock_track_status() -> DataFrame:
    return pd.DataFrame({
        "Status": [1, 2, 1],
        "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000), Timedelta(milliseconds=4000)],
    })


@pytest.fixture()
def mock_circuit_info(mocker: MockerFixture) -> MagicMock:
    circuit_info = mocker.MagicMock(spec=CircuitInfo)
    circuit_info.rotation = 45.0
    return circuit_info


@pytest.fixture()
def track_status_colors() -> DataFrame:
    return pd.DataFrame({
        "Status": [1, 2, 4, 5, 6, 7],
        "Label": [
            "Green Flag",
            "Yellow Flag",
            "Safety Car",
            "Red Flag",
            "VSC Deployed",
            "VSC Ending",
        ],
        "Color": [
            LVecBase4f(0, 1, 0, 0.8),
            LVecBase4f(1, 1, 0, 0.8),
            LVecBase4f(1, 1, 0, 0.8),
            LVecBase4f(1, 0, 0, 0.8),
            LVecBase4f(1, 0.64, 0, 0.8),
            LVecBase4f(1, 0.64, 0, 0.8),
        ],
        "TextColor": [
            LVecBase4f(0, 0, 0, 0.8),
            LVecBase4f(0, 0, 0, 0.8),
            LVecBase4f(0, 0, 0, 0.8),
            LVecBase4f(1, 1, 1, 0.8),
            LVecBase4f(0, 0, 0, 0.8),
            LVecBase4f(0, 0, 0, 0.8),
        ],
    })


@pytest.fixture()
def green_flag_track_status() -> DataFrame:
    return pd.DataFrame({
        "Status": [1],
        "Label": ["Green Flag"],
        "Color": [LVecBase4f(0, 1, 0, 0.8)],
        "TextColor": [LVecBase4f(0, 0, 0, 0.8)],
    })


@pytest.fixture()
def processed_weather_data() -> DataFrame:
    return pd.DataFrame({
        "SessionTimeTick": [1, 2, 3, 4, 5],
        "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000), Timedelta(milliseconds=3000), Timedelta(milliseconds=4000), Timedelta(milliseconds=5000)],
        "AirTemp": [20, 21, 22, 21, 20],
        "TrackTemp": [30, 31, 32, 31, 30],
    })


@pytest.fixture()
def processed_track_statuses() -> DataFrame:
    return pd.DataFrame({
        "Status": [1, 2],
        "SessionTimeTick": [1, 2],
        "SessionTimeTickEnd": [2, 4],
        "PixelStart": [0, 166.666667],
        "PixelEnd": [166.666667 ,500],
        "Width": [166.666667, 333.333333],
        "Label": ["Green Flag", "Yellow Flag"],
        "Color": [LVecBase4f(0, 1, 0, 0.8), LVecBase4f(1, 1, 0, 0.8)],
        "TextColor": [LVecBase4f(0, 0, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
    })


@pytest.fixture()
def mock_pos_data_with_session_time() -> DataFrame:
    return pd.DataFrame({
        "SessionTimeTick": [1, 2, 3, 4, 1, 2, 3],
        "SessionTime": [
            Timedelta(milliseconds=1000),
            Timedelta(milliseconds=2000),
            Timedelta(milliseconds=3000),
            Timedelta(milliseconds=4000),
            Timedelta(milliseconds=1000),
            Timedelta(milliseconds=2000),
            Timedelta(milliseconds=3000),
        ],
        "X": [1.0, 2.0, 3.0, 4.0, 1.1, 2.1, 3.1],
        "Y": [1.0, 2.0, 3.0, 4.0, 1.1, 2.1, 3.1],
        "Z": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "DriverNumber": [1, 1, 1, 1, 2, 2, 2],
    })


@pytest.fixture()
def fastest_lap_data() -> DataFrame:
    return pd.DataFrame({
        "X": [1.0, 2.0, 3.0, 4.0],
        "Y": [1.0, 2.0, 3.0, 4.0],
        "Z": [0.0, 0.0, 0.0, 0.0],
    })


@pytest.fixture()
def pos_data_dict(mocker: MockerFixture, fastest_lap_data: DataFrame) -> dict[str, Telemetry]:
    mock_telemetry_1 = mocker.MagicMock(spec=Telemetry)
    mock_telemetry_1.__getitem__ = lambda self, key: fastest_lap_data[key]
    mock_telemetry_1.columns = fastest_lap_data.columns.tolist()

    mock_telemetry_2 = mocker.MagicMock(spec=Telemetry)
    mock_telemetry_2.__getitem__ = lambda self, key: fastest_lap_data[key]
    mock_telemetry_2.columns = fastest_lap_data.columns.tolist()

    return {"1": mock_telemetry_1, "2": mock_telemetry_2}


@pytest.fixture()
def pos_data_for_filtering() -> DataFrame:
    return pd.DataFrame({
        "SessionTime": [
            Timedelta(milliseconds=500),
            Timedelta(milliseconds=1000),
            Timedelta(milliseconds=1500),
            Timedelta(milliseconds=2000),
            Timedelta(milliseconds=2500),
        ],
        "X": [1.0, 2.0, 3.0, 4.0, 5.0],
        "Y": [1.0, 2.0, 3.0, 4.0, 5.0],
        "Z": [0.0, 0.0, 0.0, 0.0, 0.0],
        "DriverNumber": [1, 1, 1, 1, 1],
    })


@pytest.fixture()
def pos_data_for_normalization() -> DataFrame:
    return pd.DataFrame({
        "SessionTime": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000)],
        "X": [1.0, 2.0],
        "Y": [1.0, 2.0],
        "Z": [0.0, 0.0],
        "DriverNumber": [1, 1],
    })


@pytest.fixture()
def pos_data_for_milliseconds() -> DataFrame:
    return pd.DataFrame({
        "SessionTime": [
            Timedelta(seconds=1),
            Timedelta(seconds=2),
            Timedelta(seconds=3),
        ],
        "X": [1.0, 2.0, 3.0],
        "Y": [1.0, 2.0, 3.0],
        "Z": [0.0, 0.0, 0.0],
        "DriverNumber": [1, 1, 1],
    })


@pytest.fixture()
def pos_data_for_session_time_tick() -> DataFrame:
    return pd.DataFrame({
        "SessionTime": [
            Timedelta(milliseconds=1000),
            Timedelta(milliseconds=2000),
            Timedelta(milliseconds=3000),
            Timedelta(milliseconds=1000),
            Timedelta(milliseconds=2000),
            Timedelta(milliseconds=3000),
        ],
        "X": [1.0, 2.0, 3.0, 1.1, 2.1, 3.1],
        "Y": [1.0, 2.0, 3.0, 1.1, 2.1, 3.1],
        "Z": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
        "DriverNumber": [1, 1, 1, 2, 2, 2],
    })
