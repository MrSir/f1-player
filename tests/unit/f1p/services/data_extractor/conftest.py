from unittest.mock import MagicMock

import pandas as pd
import pytest
from direct.task.Task import TaskManager
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
def mock_green_flag_track_status() -> DataFrame:
    return pd.DataFrame({
        "Status": [1],
        "Label": ["Green Flag"],
        "Color": [LVecBase4f(0, 1, 0, 0.8)],
        "TextColor": [LVecBase4f(0, 0, 0, 0.8)],
    })

