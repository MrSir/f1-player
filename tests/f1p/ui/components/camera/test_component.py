from unittest.mock import MagicMock

import pytest
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager, Task
from panda3d.core import MouseWatcher
from pytest_mock import MockerFixture

from f1p.ui.components.camera.component import MainCamera
from f1p.ui.components.camera.enums import CameraType
from f1p.ui.components.camera.types import CameraController, OrbitingCameraController, TopDownCameraController


@pytest.fixture()
def mock_task_manager(mocker: MockerFixture) -> MagicMock:
    m_task_manager = mocker.MagicMock(spec=TaskManager)

    return m_task_manager


@pytest.fixture()
def mock_mouse_watcher(mocker: MockerFixture) -> MagicMock:
    m_mouse_watcher = mocker.MagicMock(spec=MouseWatcher)
    m_mouse_watcher.hasMouse = mocker.MagicMock()
    m_mouse_watcher.getMouseX = mocker.MagicMock()
    m_mouse_watcher.getMouseY = mocker.MagicMock()

    return m_mouse_watcher


@pytest.fixture()
def main_camera(mock_task_manager: MagicMock, mock_mouse_watcher: MagicMock, mock_camera: MagicMock) -> MainCamera:
    return MainCamera(mock_task_manager, mock_mouse_watcher, mock_camera)


def test_initialization(
    mock_task_manager: MagicMock,
    mock_mouse_watcher: MagicMock,
    mock_camera: MagicMock,
    mocker: MockerFixture
) -> None:
    mock_accept = mocker.MagicMock()
    mocker.patch('f1p.ui.components.camera.component.DirectObject.accept', mock_accept)

    main_camera = MainCamera(mock_task_manager, mock_mouse_watcher, mock_camera)

    assert isinstance(main_camera, DirectObject)
    assert mock_task_manager == main_camera.task_manager
    assert mock_mouse_watcher == main_camera.mouse_watcher
    assert mock_camera == main_camera.camera

    assert main_camera.enabled is False

    assert {} == main_camera.camera_controllers
    assert CameraType.ORBITING == main_camera.camera_type

    assert () == main_camera.left_mouse_down_pos
    assert main_camera.can_move_camera is False

    mock_accept.assert_has_calls(
        [
            mocker.call("sessionSelected", main_camera.enable),
            mocker.call("mouse1", main_camera.left_mouse_down),
            mocker.call("mouse1-up", main_camera.left_mouse_up),
            mocker.call("wheel_up", main_camera.zoom_camera_in),
            mocker.call("wheel_down", main_camera.zoom_camera_out),
            mocker.call("switchCamera", main_camera.switch_camera),
        ]
    )


def test_configure(main_camera: MainCamera, mocker: MockerFixture) -> None:
    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_class = mocker.MagicMock(return_value=mock_orb_cam_cntr)
    mocker.patch('f1p.ui.components.camera.component.OrbitingCameraController', mock_orb_class)
    mock_td_cam_cntr = mocker.MagicMock(spec=TopDownCameraController)
    mock_td_class = mocker.MagicMock(return_value=mock_td_cam_cntr)
    mocker.patch('f1p.ui.components.camera.component.TopDownCameraController', mock_td_class)

    main_camera.configure()

    assert {
        CameraType.ORBITING: mock_orb_cam_cntr,
        CameraType.TOP_DOWN: mock_td_cam_cntr,
    } == main_camera.camera_controllers

    assert CameraType.ORBITING == main_camera.camera_type
    assert mock_orb_cam_cntr == main_camera.controller
    mock_orb_cam_cntr.re_center.assert_called_once()


def test_enable(main_camera: MainCamera, mock_task_manager: MagicMock) -> None:
    assert main_camera.enabled is False

    main_camera.enable()

    assert main_camera.enabled is True

    mock_task_manager.add.assert_called_once_with(main_camera.animate_camera, "animate_camera")


@pytest.mark.parametrize(
    ("enabled", "expected_call_count", "case"),
    [
        (False, 0, "Not enabled."),
        (True, 1, "Enabled."),
    ]
)
def test_zoom_in(enabled: bool, expected_call_count: int, case: str, main_camera: MainCamera, mocker: MockerFixture) -> None:
    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_cam_cntr.zoom_camera_in = mocker.MagicMock()

    main_camera.controller = mock_orb_cam_cntr

    main_camera.enabled = enabled

    main_camera.zoom_camera_in()

    assert expected_call_count == mock_orb_cam_cntr.zoom_camera_in.call_count, case


@pytest.mark.parametrize(
    ("enabled", "expected_call_count", "case"),
    [
        (False, 0, "Not enabled."),
        (True, 1, "Enabled."),
    ]
)
def test_zoom_out(enabled: bool, expected_call_count: int, case: str, main_camera: MainCamera, mocker: MockerFixture) -> None:
    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_cam_cntr.zoom_camera_out = mocker.MagicMock()

    main_camera.controller = mock_orb_cam_cntr

    main_camera.enabled = enabled

    main_camera.zoom_camera_out()

    assert expected_call_count == mock_orb_cam_cntr.zoom_camera_out.call_count, case


def test_switch_camera(main_camera: MainCamera, mocker: MockerFixture) -> None:
    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_td_cam_cntr = mocker.MagicMock(spec=TopDownCameraController)

    main_camera.camera_controllers = {
        CameraType.ORBITING: mock_orb_cam_cntr,
        CameraType.TOP_DOWN: mock_td_cam_cntr,
    }

    main_camera.switch_camera(CameraType.ORBITING)
    assert mock_orb_cam_cntr == main_camera.controller
    mock_orb_cam_cntr.re_center.assert_called_once()

    main_camera.switch_camera(CameraType.TOP_DOWN)
    assert mock_td_cam_cntr == main_camera.controller
    mock_td_cam_cntr.re_center.assert_called_once()


def test_animate_camera(main_camera: MainCamera, mocker: MockerFixture) -> None:
    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    main_camera.controller = mock_orb_cam_cntr

    mock_task = mocker.MagicMock(spec=Task)

    assert mock_task.cont == main_camera.animate_camera(mock_task)

    mock_orb_cam_cntr.animate_camera.assert_called_once()


def test_left_mouse_down_not_in_screen(main_camera: MainCamera, mock_mouse_watcher: MagicMock, mock_task_manager: MagicMock) -> None:
    mock_mouse_watcher.hasMouse.return_value = False

    assert main_camera.can_move_camera is False
    assert () == main_camera.left_mouse_down_pos

    main_camera.left_mouse_down()

    mock_mouse_watcher.hasMouse.assert_called_once()
    mock_mouse_watcher.getMouseX.assert_not_called()
    mock_mouse_watcher.getMouseY.assert_not_called()

    assert () == main_camera.left_mouse_down_pos
    assert main_camera.can_move_camera is False

    mock_task_manager.add.assert_not_called()


def test_left_mouse_down_in_screen(main_camera: MainCamera, mock_mouse_watcher: MagicMock, mock_task_manager: MagicMock) -> None:
    mock_mouse_watcher.hasMouse.return_value = True

    assert main_camera.can_move_camera is False
    assert () == main_camera.left_mouse_down_pos

    main_camera.left_mouse_down()

    mock_mouse_watcher.hasMouse.assert_called_once()
    mock_mouse_watcher.getMouseX.assert_called_once()
    mock_mouse_watcher.getMouseY.assert_called_once()

    assert (mock_mouse_watcher.getMouseX.return_value, mock_mouse_watcher.getMouseY.return_value) == main_camera.left_mouse_down_pos
    assert main_camera.can_move_camera is True

    mock_task_manager.add.assert_called_once_with(main_camera.move_camera, "move_camera")


def test_left_mouse_up(main_camera: MainCamera) -> None:
    main_camera.can_move_camera = True

    main_camera.left_mouse_up()

    assert main_camera.can_move_camera is False


def test_move_camera_cannot_move(main_camera: MainCamera, mock_mouse_watcher: MagicMock, mocker: MockerFixture) -> None:
    mock_task = mocker.MagicMock(spec=Task)

    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_cam_cntr.mouse_x = 0
    mock_orb_cam_cntr.mouse_y = 0
    main_camera.controller = mock_orb_cam_cntr

    main_camera.can_move_camera = False
    assert mock_task.done == main_camera.move_camera(mock_task)

    mock_mouse_watcher.hasMouse.assert_not_called()
    mock_mouse_watcher.getMouseX.assert_not_called()
    mock_mouse_watcher.getMouseY.assert_not_called()
    mock_orb_cam_cntr.move_camera.assert_not_called()
    assert 0 == mock_orb_cam_cntr.mouse_x
    assert 0 == mock_orb_cam_cntr.mouse_y


def test_move_camera_can_move(main_camera: MainCamera, mock_mouse_watcher: MagicMock, mocker: MockerFixture) -> None:
    mock_task = mocker.MagicMock(spec=Task)

    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_cam_cntr.mouse_x = 0
    mock_orb_cam_cntr.mouse_y = 0
    main_camera.controller = mock_orb_cam_cntr

    mock_mouse_watcher.hasMouse.return_value = True

    main_camera.can_move_camera = True
    assert mock_task.cont == main_camera.move_camera(mock_task)

    mock_mouse_watcher.hasMouse.assert_called_once()
    mock_mouse_watcher.getMouseX.assert_called_once()
    mock_mouse_watcher.getMouseY.assert_called_once()
    mock_orb_cam_cntr.move_camera.assert_called_once()
    assert mock_mouse_watcher.getMouseX.return_value == mock_orb_cam_cntr.mouse_x
    assert mock_mouse_watcher.getMouseY.return_value == mock_orb_cam_cntr.mouse_y


def test_move_camera_can_move_not_on_screen(main_camera: MainCamera, mock_mouse_watcher: MagicMock, mocker: MockerFixture) -> None:
    mock_task = mocker.MagicMock(spec=Task)

    mock_orb_cam_cntr = mocker.MagicMock(spec=OrbitingCameraController)
    mock_orb_cam_cntr.mouse_x = 0
    mock_orb_cam_cntr.mouse_y = 0
    main_camera.controller = mock_orb_cam_cntr

    mock_mouse_watcher.hasMouse.return_value = False

    main_camera.can_move_camera = True
    assert mock_task.cont == main_camera.move_camera(mock_task)

    mock_mouse_watcher.hasMouse.assert_called_once()
    mock_mouse_watcher.getMouseX.assert_not_called()
    mock_mouse_watcher.getMouseY.assert_not_called()
    mock_orb_cam_cntr.move_camera.assert_not_called()
    assert 0 == mock_orb_cam_cntr.mouse_x
    assert 0 == mock_orb_cam_cntr.mouse_y
