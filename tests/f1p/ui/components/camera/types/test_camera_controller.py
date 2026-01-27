from unittest.mock import MagicMock

import pytest
from pytest_mock import MockerFixture

from f1p.ui.components.camera.types import CameraController


@pytest.fixture()
def camera_controller(mock_camera: MagicMock) -> CameraController:
    return CameraController(mock_camera, (1, 2, 3))


def test_initialization(mock_camera: MagicMock) -> None:
    pos = (1, 2, 3)
    look_at = (4, 5, 6)

    controller = CameraController(mock_camera, pos, look_at=look_at)

    assert mock_camera == controller.camera
    assert pos == controller.default_pos
    assert look_at == controller.default_look_at
    assert 0 == controller.zoom
    assert 0 == controller.mouse_x
    assert 0 == controller.mouse_y

    assert hasattr(controller, "animate_camera")
    assert hasattr(controller, "move_camera")


def test_initialization_without_look_at(mock_camera: MagicMock) -> None:
    pos = (1, 2, 3)

    controller = CameraController(mock_camera, pos)

    assert mock_camera == controller.camera
    assert pos == controller.default_pos
    assert (0, 0, 0) == controller.default_look_at
    assert 0 == controller.zoom
    assert 0 == controller.mouse_x
    assert 0 == controller.mouse_y

    assert hasattr(controller, "animate_camera")
    assert hasattr(controller, "move_camera")


def test_re_center(camera_controller: CameraController, mock_camera: MagicMock) -> None:
    camera_controller.re_center()

    mock_camera.setPos.assert_called_with(*camera_controller.default_pos)
    mock_camera.lookAt.assert_called_with(*camera_controller.default_look_at)


@pytest.mark.parametrize(
    ("initial_zoom", "expected_zoom", "expected_calls_to_move", "case"),
    [
        (0, 1, 1, "Zoom is incremented."),
        (100, 100, 0, "Zoom is capped at 100."),
    ],
)
def test_zoom_camera_in(
    initial_zoom: int,
    expected_zoom: int,
    expected_calls_to_move: int,
    case: str,
    camera_controller: CameraController,
    mocker: MockerFixture,
) -> None:
    mock_move_camera = mocker.patch.object(camera_controller, "move_camera")

    camera_controller.zoom = initial_zoom
    assert initial_zoom == camera_controller.zoom

    camera_controller.zoom_camera_in()

    assert expected_zoom == camera_controller.zoom, case
    assert expected_calls_to_move == mock_move_camera.call_count


@pytest.mark.parametrize(
    ("initial_zoom", "expected_zoom", "expected_calls_to_move", "case"),
    [
        (100, 99, 1, "Zoom is decremented."),
        (10, 10, 0, "Zoom is capped at 10."),
    ],
)
def test_zoom_camera_out(
    initial_zoom: int,
    expected_zoom: int,
    expected_calls_to_move: int,
    case: str,
    camera_controller: CameraController,
    mocker: MockerFixture,
) -> None:
    mock_move_camera = mocker.patch.object(camera_controller, "move_camera")

    camera_controller.zoom = initial_zoom
    assert initial_zoom == camera_controller.zoom

    camera_controller.zoom_camera_out()

    assert expected_zoom == camera_controller.zoom, case
    assert expected_calls_to_move == mock_move_camera.call_count
