from unittest.mock import MagicMock

import pytest
from panda3d.core import Camera
from pytest_mock import MockerFixture

from f1p.ui.components.camera.types import CameraController, TopDownCameraController


@pytest.fixture()
def mock_camera(mocker: MockerFixture) -> MagicMock:
    m_camera = mocker.MagicMock(spec=Camera)
    m_camera.setPos = mocker.MagicMock()
    m_camera.lookAt = mocker.MagicMock()

    return m_camera


@pytest.fixture()
def camera_controller(mock_camera: MagicMock) -> TopDownCameraController:
    return TopDownCameraController(mock_camera)


def test_initialization(mock_camera: MagicMock) -> None:
    controller = TopDownCameraController(mock_camera)

    assert isinstance(controller, CameraController)
    assert mock_camera == controller.camera
    assert (0, 0, 100) == controller.default_pos
    assert (0, 0, 0) == controller.default_look_at
    assert 0 == controller.zoom
