from unittest.mock import MagicMock

import pytest
from direct.task.Task import TaskManager
from panda3d.core import NodePath
from pytest_mock import MockerFixture

from f1p.app import F1PlayerApp
from f1p.services.data_extractor.service import DataExtractorService


@pytest.fixture
def mock_parent(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=NodePath)


@pytest.fixture()
def mock_task_manager(mocker: MockerFixture) -> MagicMock:
    m_task_manager = mocker.MagicMock(spec=TaskManager)

    return m_task_manager


@pytest.fixture()
def mock_data_extractor(mocker: MockerFixture) -> MagicMock:
    return mocker.MagicMock(spec=DataExtractorService)


@pytest.fixture()
def mock_f1p_app(mock_task_manager: MagicMock, mocker: MockerFixture) -> MagicMock:
    m = mocker.MagicMock(spec=F1PlayerApp)
    m.render = mocker.MagicMock(spec=NodePath)
    m.taskMgr = mock_task_manager

    return m
