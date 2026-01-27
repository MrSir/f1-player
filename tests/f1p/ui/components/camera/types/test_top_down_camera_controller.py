from unittest.mock import MagicMock

import pytest

from f1p.ui.components.camera.types import CameraController, TopDownCameraController


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
    assert 0 == controller.mouse_x
    assert 0 == controller.mouse_y


@pytest.mark.parametrize(
    ("zoom", "mouse_x", "mouse_y", "default_pos", "default_look_at", "pos", "look_at"),
    [
        (0, 0, 0, (0, 0, 100), (0, 0, 0), (0, 0, 100), (0, 0, 0)),
        (10, 0, 0, (0, 0, 100), (0, 0, 0), (0, 0, 90), (0, 0, 0)),
        (0, 0.5, 0, (0, 0, 100), (0, 0, 0), (-5, 0, 100), (-5, 0, 0)),
        (0, 0, 0.5, (0, 0, 100), (0, 0, 0), (0, -5, 100), (0, -5, 0)),
        (50, -0.5, -0.5, (0, 0, 100), (0, 0, 0), (5, 5, 50), (5, 5, 0)),
        (50, -0.5, -0.5, (15, 15, 100), (0, 0, 0), (12.5, 12.5, 50), (5, 5, 0)),
    ],
)
def test_move_camera(
    zoom: int,
    mouse_x: float,
    mouse_y: float,
    default_pos: tuple[float, float, float],
    default_look_at: tuple[float, float, float],
    pos: tuple[float, float, float],
    look_at: tuple[float, float, float],
    camera_controller: TopDownCameraController,
    mock_camera: MagicMock,
) -> None:
    camera_controller.zoom = zoom
    camera_controller.mouse_x = mouse_x
    camera_controller.mouse_y = mouse_y
    camera_controller.default_pos = default_pos
    camera_controller.default_look_at = default_look_at

    camera_controller.move_camera()

    mock_camera.setPos.assert_called_once_with(*pos)
    mock_camera.lookAt.assert_called_once_with(*look_at)
