from unittest.mock import MagicMock

import pytest
from panda3d.core import Camera
from pytest_mock import MockerFixture


@pytest.fixture()
def mock_camera(mocker: MockerFixture) -> MagicMock:
    m_camera = mocker.MagicMock(spec=Camera)
    m_camera.setPos = mocker.MagicMock()
    m_camera.lookAt = mocker.MagicMock()
    m_camera.getX = mocker.MagicMock()
    m_camera.getY = mocker.MagicMock()
    m_camera.setX = mocker.MagicMock()
    m_camera.setY = mocker.MagicMock()

    return m_camera
