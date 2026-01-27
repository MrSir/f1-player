import math
from unittest.mock import MagicMock

import pytest
from panda3d.core import deg2Rad

from f1p.ui.components.camera.types import CameraController, OrbitingCameraController


@pytest.fixture()
def camera_controller(mock_camera: MagicMock) -> OrbitingCameraController:
    return OrbitingCameraController(mock_camera)


def test_initialization(mock_camera: MagicMock) -> None:
    controller = OrbitingCameraController(mock_camera)

    assert isinstance(controller, CameraController)
    assert mock_camera == controller.camera
    assert (0, -70, 40) == controller.default_pos
    assert (0, 0, 0) == controller.default_look_at
    assert 0 == controller.zoom
    assert 0 == controller.mouse_x
    assert 0 == controller.mouse_y


@pytest.mark.parametrize(
    ("x", "y", "rad", "expected_x", "expected_y", "case"),
    [
        (0, 0, 0, 0, 0, "Nothing to rotate"),
        (10, 10, math.pi, -10, -10, "Rotate 180 deg."),
        (10, 10, math.pi / 2, -10, 10, "Rotate 90 deg."),
    ],
)
def test_rotate_around_z(
    x: float,
    y: float,
    rad: float,
    expected_x: float,
    expected_y: float,
    case: str,
) -> None:
    actual_x, actual_y = OrbitingCameraController.rotate_around_z(x, y, rad)

    assert expected_x == pytest.approx(actual_x), case
    assert expected_y == pytest.approx(actual_y), case


@pytest.mark.parametrize(
    ("initial_rotation", "rotation_after"),
    [
        (0, deg2Rad(0.3)),
        (math.pi, math.pi + deg2Rad(0.3)),
    ],
)
def test_animate_camera(
    initial_rotation: float,
    rotation_after: float,
    camera_controller: OrbitingCameraController,
    mock_camera: MagicMock,
) -> None:
    mock_camera.getX.return_value = 10
    mock_camera.getY.return_value = 10

    camera_controller.rotation = initial_rotation
    camera_controller.animate_camera()

    assert rotation_after == camera_controller.rotation

    mock_camera.getX.assert_called_once()
    mock_camera.getY.assert_called_once()

    mock_camera.setX.assert_called_once_with(9.947503284160073)
    mock_camera.setY.assert_called_once_with(10.052222560788463)
    mock_camera.lookAt.assert_called_once_with(*camera_controller.default_look_at)


@pytest.mark.parametrize(
    ("zoom", "mouse_y", "default_pos", "default_look_at", "pos", "look_at"),
    [
        (0, 0, (0, 0, 100), (0, 0, 0), (0, 0, 100), (0, 0, 0)),
        (10, 0, (0, 0, 100), (0, 0, 0), (0, 0, 90), (0, 0, 0)),
        (0, 0.5, (0, 0, 100), (0, 0, 0), (0, 0, 95), (0, 0, 0)),
        (50, -0.5, (0, 0, 100), (0, 0, 0), (0, 0, 55), (0, 0, 0)),
        (50, -0.5, (15, 15, 100), (0, 0, 0), (7.5, 7.5, 55), (0, 0, 0)),
    ],
)
def test_move_camera(
    zoom: int,
    mouse_y: float,
    default_pos: tuple[float, float, float],
    default_look_at: tuple[float, float, float],
    pos: tuple[float, float, float],
    look_at: tuple[float, float, float],
    camera_controller: OrbitingCameraController,
    mock_camera: MagicMock,
) -> None:
    camera_controller.zoom = zoom
    camera_controller.mouse_y = mouse_y
    camera_controller.default_pos = default_pos
    camera_controller.default_look_at = default_look_at

    camera_controller.move_camera()

    mock_camera.setPos.assert_called_once_with(*pos)
    mock_camera.lookAt.assert_called_once_with(*look_at)
