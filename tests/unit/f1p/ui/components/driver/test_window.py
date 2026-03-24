from unittest.mock import MagicMock

import pytest
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from panda3d.core import (
    Camera,
    GraphicsWindow,
    LVecBase4f,
    NodePath,
    PerspectiveLens,
    PGTop,
    Point3,
    TextNode,
    VBase4,
    Vec4,
    WindowProperties,
)
from pytest_mock import MockerFixture

from f1p.ui.components.driver.window import DriverWindow
from f1p.ui.enums import Colors


@pytest.fixture
def team_color() -> LVecBase4f:
    return LVecBase4f(1, 0, 0, 0.8)


@pytest.fixture
def strategy() -> dict[int, dict[str, str | int]]:
    return {
        1: {"Compound": "S", "CompoundColor": LVecBase4f(1, 0, 0, 0.8), "LapNumber": 10, "TotalLaps": 60},
        2: {"Compound": "M", "CompoundColor": LVecBase4f(1, 1, 0, 0.8), "LapNumber": 20, "TotalLaps": 60},
    }


@pytest.fixture
def driver_window(
    mock_f1p_app: MagicMock,
    team_color: LVecBase4f,
    mock_data_extractor: MagicMock,
) -> DriverWindow:
    return DriverWindow(
        800,
        900,
        "1",
        f"Joe",
        "Shmoe",
        team_color,
        "Team 1",
        mock_f1p_app,
        mock_data_extractor,
    )


def test_init(
    mock_f1p_app: MagicMock,
    team_color: LVecBase4f,
    mock_data_extractor: MagicMock,
    mocker: MockerFixture,
) -> None:
    width = 800
    height = 600
    driver_number = "1"
    first_name = "Joe"
    last_name = "Shmoe"
    team_name = "Rd Bull Racing"

    mock_accept = mocker.MagicMock()
    mocker.patch("f1p.ui.components.driver.window.DriverWindow.accept", mock_accept)

    driver_window = DriverWindow(
        width,
        height,
        driver_number,
        first_name,
        last_name,
        team_color,
        team_name,
        mock_f1p_app,
        mock_data_extractor,
    )

    assert driver_window.width == width
    assert driver_window.height == height
    assert driver_window.driver_frame_height == 345
    assert driver_window.telemetry_frame_height == 225
    assert driver_window.tire_strategy_height == 90
    assert driver_window.laps_widget_width == 510

    assert driver_window.driver_number == driver_number
    assert driver_window.first_name == first_name
    assert driver_window.last_name == last_name
    assert driver_window.team_color_obj == team_color
    assert driver_window.team_name == team_name
    assert driver_window.app is mock_f1p_app
    assert driver_window.data_extractor == mock_data_extractor

    assert mock_data_extractor.total_laps == driver_window.total_laps
    assert driver_window.is_open is False

    assert driver_window._strategy is None
    assert driver_window._driver_laps is None
    assert driver_window._lap_averages is None
    assert driver_window._slowest_non_pit_lap is None
    assert driver_window._slowest_driver_lap is None
    assert driver_window._fastest_driver_lap is None
    assert driver_window._window_properties is None
    assert driver_window._window is None

    assert driver_window._render2d is None
    assert driver_window._pixel2d is None

    assert driver_window._lens is None
    assert driver_window._camera is None
    assert driver_window._camera_np is None

    assert driver_window.position is None
    assert driver_window.laps is None
    assert driver_window.speed_kph is None
    assert driver_window.speed_mph is None
    assert driver_window.rpm is None
    assert driver_window.gear_N is None
    assert driver_window.gear_1 is None
    assert driver_window.gear_2 is None
    assert driver_window.gear_3 is None
    assert driver_window.gear_4 is None
    assert driver_window.gear_5 is None
    assert driver_window.gear_6 is None
    assert driver_window.gear_7 is None
    assert driver_window.gear_8 is None
    assert driver_window.drs is None
    assert driver_window.brake is None
    assert driver_window.throttle is None
    assert driver_window.lap_time_line is None

    assert driver_window.previous_lap_number is None
    assert driver_window.previous_s1_frame is None
    assert driver_window.previous_s1_time is None
    assert driver_window.previous_s2_frame is None
    assert driver_window.previous_s2_time is None
    assert driver_window.previous_s3_frame is None
    assert driver_window.previous_s3_time is None
    assert driver_window.previous_lap_time is None
    assert driver_window.previous_lap_time_percent is None

    assert driver_window.lap_number == 0
    assert driver_window.previous_lap is None
    assert driver_window.current_lap_number is None
    assert driver_window.current_s1_frame is None
    assert driver_window.current_s1_time is None
    assert driver_window.current_s2_frame is None
    assert driver_window.current_s2_time is None
    assert driver_window.current_s3_frame is None
    assert driver_window.current_s3_time is None
    assert driver_window.current_lap_time is None

    assert isinstance(driver_window, DirectObject)
    mock_accept.assert_called_once_with(f"closeDriver{driver_number}", driver_window.close)


def test_window_properties_creates_properties_on_first_access(
    driver_window: DriverWindow,
) -> None:
    props = driver_window.window_properties

    assert isinstance(props, WindowProperties)
    assert driver_window._window_properties == props

    width, height = props.getSize()
    assert width == 800
    assert height == 900

    assert props.getFixedSize() is True
    assert "Driver 1 - Joe Shmoe" in props.getTitle()


def test_window_properties_returns_cached_instance(driver_window: DriverWindow, mocker: MagicMock) -> None:
    mock_window_properties = mocker.MagicMock(spec=WindowProperties)

    driver_window._window_properties = mock_window_properties

    assert mock_window_properties == driver_window.window_properties


def test_window_creates_window_on_first_access(
    driver_window: DriverWindow,
    mock_f1p_app: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    mock_f1p_app.openWindow.return_value = mock_window

    window = driver_window.window

    assert window is mock_window
    mock_f1p_app.openWindow.assert_called_once()
    mock_window.setCloseRequestEvent.assert_called_once_with(f"closeDriver{driver_window.driver_number}")
    mock_window.setClearColor.assert_called_once_with(VBase4(0.3, 0.3, 0.3, 1))


def test_window_returns_cached_instance(
    driver_window: DriverWindow,
    mock_f1p_app: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    driver_window._window = mock_window

    assert mock_window == driver_window.window
    mock_f1p_app.openWindow.assert_not_called()


def test_render2d_creates_render_node_on_first_access(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    driver_window._window = mock_window
    mock_camera_2d = mocker.MagicMock(spec=NodePath)
    driver_window.app.makeCamera2d.return_value = mock_camera_2d

    render2d = driver_window.render2d

    assert isinstance(render2d, NodePath)
    assert driver_window._render2d == render2d
    assert render2d.getDepthTest() is False
    assert render2d.getDepthWrite() is False

    driver_window.app.makeCamera2d.assert_called_once_with(mock_window)
    mock_camera_2d.reparentTo.assert_called_once_with(render2d)


def test_render2d_returns_cached_instance(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_render2d = mocker.MagicMock(spec=NodePath)

    driver_window._render2d = mock_render2d
    assert mock_render2d == driver_window.render2d


def test_pixel2d_creates_pixel_node_on_first_access(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_pixel2d = mocker.MagicMock(spec=NodePath)
    mock_render2d = mocker.MagicMock(spec=NodePath)
    mock_render2d.attachNewNode.return_value = mock_pixel2d
    driver_window._render2d = mock_render2d

    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    mock_window.getSize.return_value = (driver_window.width, driver_window.height)
    driver_window._window = mock_window

    mock_pgtop = mocker.MagicMock(spec=PGTop)
    mock_pgtop_class = mocker.MagicMock(spec=PGTop, return_value=mock_pgtop)
    mocker.patch("f1p.ui.components.driver.window.PGTop", mock_pgtop_class)

    pixel2d = driver_window.pixel2d

    assert isinstance(pixel2d, NodePath)
    assert mock_pixel2d == pixel2d
    assert mock_pixel2d == driver_window._pixel2d

    mock_pgtop_class.assert_called_once_with(f"pixel2d{driver_window.driver_number}")
    mock_render2d.attachNewNode.assert_called_once_with(mock_pgtop)
    mock_pixel2d.setPos.assert_called_once_with(-1, 0, 1)
    mock_pixel2d.setScale.assert_called_once_with(2.0 / driver_window.width, 1.0, 2.0 / driver_window.height)
    mock_pixel2d.reparentTo.assert_called_once_with(mock_render2d)


def test_pixel2d_returns_cached_instance(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_pixel2d = mocker.MagicMock(spec=NodePath)

    driver_window._pixel2d = mock_pixel2d
    pixel2d2 = driver_window.pixel2d

    assert mock_pixel2d == pixel2d2


def test_lens_creates_lens_on_first_access(
    driver_window: DriverWindow,
) -> None:
    lens = driver_window.lens

    assert isinstance(lens, PerspectiveLens)
    assert driver_window._lens == lens
    assert lens.getAspectRatio() == pytest.approx(640 / 480)


def test_lens_returns_cached_instance(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_lens = mocker.MagicMock(spec=PerspectiveLens)
    driver_window._lens = mock_lens
    lens = driver_window.lens

    assert mock_lens == lens


def test_camera_creates_camera_on_first_access(
    driver_window: DriverWindow,
) -> None:
    lens = PerspectiveLens()
    driver_window._lens = lens
    camera = driver_window.camera

    assert isinstance(camera, Camera)
    assert driver_window._camera == camera
    assert lens == camera.getLens()


def test_camera_returns_cached_instance(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_camera = mocker.MagicMock(spec=Camera)
    driver_window._camera = mock_camera
    camera = driver_window.camera

    assert mock_camera == camera


def test_camera_np_creates_node_path_on_first_access(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_camera = mocker.MagicMock(spec=Camera)
    driver_window._camera = mock_camera
    mock_np = mocker.MagicMock(spec=NodePath)
    mock_np_class = mocker.MagicMock(spec=NodePath, return_value=mock_np)
    mocker.patch("f1p.ui.components.driver.window.NodePath", mock_np_class)

    camera_np = driver_window.camera_np

    assert isinstance(camera_np, NodePath)
    assert driver_window._camera_np == camera_np

    mock_np_class.assert_called_once_with(mock_camera)
    mock_np.reparentTo.assert_called_once_with(driver_window.app.render)


def test_camera_np_returns_cached_instance(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_np = mocker.MagicMock(spec=NodePath)
    driver_window._camera_np = mock_np
    camera_np = driver_window.camera_np

    assert mock_np == camera_np


def test_make_camera_region(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    mock_display_region = mocker.MagicMock()
    mock_window.makeDisplayRegion.return_value = mock_display_region
    driver_window._window = mock_window

    mock_camera_np = mocker.MagicMock(spec=NodePath)
    driver_window._camera_np = mock_camera_np

    driver_window.make_camera_region()

    width = 240
    padding_x = 10
    height = 240
    padding_y = 105

    mock_window.makeDisplayRegion.assert_called_once_with(
        (driver_window.width - width - (padding_x * 2)) / driver_window.width,
        (driver_window.width - (padding_x * 2)) / driver_window.width,
        (driver_window.height - padding_y - height) / driver_window.height,
        (driver_window.height - padding_y) / driver_window.height,
    )
    mock_display_region.setSort.assert_called_once_with(10)
    mock_display_region.setClearColorActive.assert_called_once_with(True)
    mock_display_region.setClearColor.assert_called_once_with(Vec4(0.3, 0.3, 0.3, 1))
    mock_display_region.setCamera.assert_called_once_with(mock_camera_np)


def test_make_driver_widget(
    driver_window: DriverWindow,
    mock_f1p_app: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_f1p_app.text_font = mocker.MagicMock()

    mock_pixel2d = mocker.MagicMock(spec=NodePath)
    driver_window._pixel2d = mock_pixel2d

    mock_direct_frame = mocker.MagicMock(spec=DirectFrame)
    mock_direct_frame_class = mocker.MagicMock(return_value=mock_direct_frame)
    mocker.patch("f1p.ui.components.driver.window.DirectFrame", mock_direct_frame_class)

    mock_onscreen_text = mocker.MagicMock(spec=OnscreenText)
    mock_onscreen_text_class = mocker.MagicMock(return_value=mock_onscreen_text)
    mocker.patch("f1p.ui.components.driver.window.OnscreenText", mock_onscreen_text_class)

    driver_window.make_driver_widget()

    title_frame_height = 30
    mock_direct_frame_class.assert_has_calls([
        mocker.call(
            parent=mock_pixel2d,
            frameColor=Colors.DARKER_GRAY,
            frameSize=(0, 260, 0, driver_window.driver_frame_height),
            pos=Point3(
                530,
                0,
                -(driver_window.height - (driver_window.height - driver_window.driver_frame_height - 10)),
            ),
            sortOrder=0,
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.BLACK,
            frameSize=(0, 260, 0, title_frame_height),
            pos=Point3(0, 0, driver_window.driver_frame_height - title_frame_height),
            sortOrder=10,
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=driver_window.team_color_obj,
            frameSize=(0, 19, 0, 19),
            pos=(10, 0, driver_window.driver_frame_height - title_frame_height - 54),
            sortOrder=20,
        ),
    ])
    mock_onscreen_text_class.assert_has_calls([
        mocker.call(
            parent=mock_direct_frame,
            text="DRIVER",
            align=TextNode.ACenter,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(260 / 2, title_frame_height - 20, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text=f"#{driver_window.driver_number} {driver_window.first_name} {driver_window.last_name}",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(10, driver_window.driver_frame_height - title_frame_height - 25, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text=driver_window.team_name,
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(33, driver_window.driver_frame_height - title_frame_height - 50, 0),
        ),
    ])


def test_make_telemetry_widget(
    driver_window: DriverWindow,
    mock_f1p_app: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_f1p_app.text_font = mocker.MagicMock()

    mock_pixel2d = mocker.MagicMock(spec=NodePath)
    driver_window._pixel2d = mock_pixel2d

    mock_direct_frame = mocker.MagicMock(spec=DirectFrame)
    mock_direct_frame_class = mocker.MagicMock(return_value=mock_direct_frame)
    mocker.patch("f1p.ui.components.driver.window.DirectFrame", mock_direct_frame_class)

    mock_onscreen_text = mocker.MagicMock(spec=OnscreenText)
    mock_onscreen_text_class = mocker.MagicMock(return_value=mock_onscreen_text)
    mocker.patch("f1p.ui.components.driver.window.OnscreenText", mock_onscreen_text_class)

    driver_window.make_telemetry_widget()

    width = 260
    title_frame_height = 30
    frame_z = -(
        driver_window.height
        - (driver_window.height - driver_window.telemetry_frame_height - driver_window.driver_frame_height - 20)
    )
    gear_spacer = 20
    initial_space = 45

    mock_direct_frame_class.assert_has_calls([
        mocker.call(
            parent=mock_pixel2d,
            frameColor=Colors.DARKER_GRAY,
            frameSize=(0, width, 0, driver_window.telemetry_frame_height),
            pos=Point3(530, 0, frame_z),
            sortOrder=0,
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.BLACK,
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, driver_window.telemetry_frame_height - title_frame_height),
            sortOrder=10,
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.GRAY,
            frameSize=(0, 240, 0, 10),
            pos=Point3(10, 0, driver_window.telemetry_frame_height - title_frame_height - 60),
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.LIGHT_BLUE,
            frameSize=(0, 0, 0, 10),
            pos=Point3(0, 0, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.GRAY,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(60, 0, driver_window.telemetry_frame_height - title_frame_height - 170),
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.LIGHT_RED,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.GRAY,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(width - 60, 0, driver_window.telemetry_frame_height - title_frame_height - 170),
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.GREEN,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        ),
    ])

    mock_onscreen_text_class.assert_has_calls([
        mocker.call(
            parent=mock_direct_frame,
            text="TELEMETRY",
            align=TextNode.ACenter,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(width / 2, title_frame_height - 21, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="GEARS",
            align=TextNode.ACenter,
            scale=13,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 20, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="N",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.GREEN,
            pos=(initial_space, driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="1",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 1), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="2",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 2), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="3",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 3), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="4",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 4), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="5",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 5), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="6",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 6), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="7",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 7), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="8",
            align=TextNode.ALeft,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(initial_space + (gear_spacer * 8), driver_window.telemetry_frame_height - title_frame_height - 40, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="0",
            align=TextNode.ALeft,
            scale=11,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(10, driver_window.telemetry_frame_height - title_frame_height - 70, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="15",
            align=TextNode.ARight,
            scale=11,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(width - 10, driver_window.telemetry_frame_height - title_frame_height - 70, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="RPM x1000",
            align=TextNode.ACenter,
            scale=11,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 70, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="BRAKE",
            align=TextNode.ACenter,
            scale=13,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(60, driver_window.telemetry_frame_height - title_frame_height - 185, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="KM/H",
            align=TextNode.ACenter,
            scale=15,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 90, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="0",
            align=TextNode.ACenter,
            scale=18,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 110, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="DRS",
            align=TextNode.ACenter,
            scale=14,
            font=driver_window.app.text_font,
            fg=Colors.GRAY,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 132, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="0",
            align=TextNode.ACenter,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.DARK_GRAY,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 155, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="MPH",
            align=TextNode.ACenter,
            scale=13,
            font=driver_window.app.text_font,
            fg=Colors.DARK_GRAY,
            pos=(width / 2, driver_window.telemetry_frame_height - title_frame_height - 170, 0),
        ),
        mocker.call(
            parent=mock_direct_frame,
            text="THROTTLE",
            align=TextNode.ACenter,
            scale=13,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(width - 60, driver_window.telemetry_frame_height - title_frame_height - 185, 0),
        ),
    ])


def test_make_tire_strategy_widget(
    driver_window: DriverWindow,
    mock_f1p_app: MagicMock,
    strategy: dict,
    mocker: MockerFixture,
) -> None:
    mock_f1p_app.text_font = mocker.MagicMock()

    mock_pixel2d = mocker.MagicMock(spec=NodePath)
    driver_window._pixel2d = mock_pixel2d

    mock_direct_frame = mocker.MagicMock(spec=DirectFrame)
    mock_direct_frame_class = mocker.MagicMock(return_value=mock_direct_frame)
    mocker.patch("f1p.ui.components.driver.window.DirectFrame", mock_direct_frame_class)

    mock_onscreen_text = mocker.MagicMock(spec=OnscreenText)
    mock_onscreen_text_class = mocker.MagicMock(return_value=mock_onscreen_text)
    mocker.patch("f1p.ui.components.driver.window.OnscreenText", mock_onscreen_text_class)

    driver_window._strategy = strategy

    driver_window.make_tire_strategy_widget()

    width = 260
    title_frame_height = 30
    frame_z = -(
        driver_window.height
        - (
            driver_window.height
            - driver_window.tire_strategy_height
            - driver_window.driver_frame_height
            - driver_window.telemetry_frame_height
            - 30
        )
    )
    padding = 10
    total_width = width - (padding * 2)
    total_laps = max(i["TotalLaps"] for i in driver_window.strategy.values())

    start = padding
    expected_direct_frame_calls = [
        mocker.call(
            parent=mock_pixel2d,
            frameColor=Colors.DARKER_GRAY,
            frameSize=(0, width, 0, driver_window.tire_strategy_height),
            pos=Point3(530, 0, frame_z),
            sortOrder=0,
        ),
        mocker.call(
            parent=mock_direct_frame,
            frameColor=Colors.BLACK,
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, driver_window.tire_strategy_height - title_frame_height),
            sortOrder=10,
        ),
    ]

    for _, info in driver_window.strategy.items():
        current_ratio = info["LapNumber"] / total_laps
        end = padding + (total_width * current_ratio)

        expected_direct_frame_calls.append(
            mocker.call(
                parent=mock_direct_frame,
                frameColor=(0.4, 0.4, 0.4, 1),
                frameSize=(start, end, 0, 30),
                pos=Point3(0, 0, driver_window.tire_strategy_height - title_frame_height - 40),
            ),
        )
        expected_direct_frame_calls.append(
            mocker.call(
                parent=mock_direct_frame,
                frameColor=info["CompoundColor"],
                frameSize=(start + 1, end - 1, 1, 29),
                pos=Point3(1, 0, driver_window.tire_strategy_height - title_frame_height - 41),
            ),
        )
        start = end

    mock_direct_frame_class.assert_has_calls(expected_direct_frame_calls)

    expected_onscreen_text_calls = [
        mocker.call(
            parent=mock_direct_frame,
            text="TIRE STRATEGY",
            align=TextNode.ACenter,
            scale=16,
            font=driver_window.app.text_font,
            fg=Colors.WHITE,
            pos=(width / 2, title_frame_height - 21, 0),
        ),
    ]

    for _, info in driver_window.strategy.items():
        current_ratio = info["LapNumber"] / total_laps
        end = padding + (total_width * current_ratio)

        expected_onscreen_text_calls.append(
            mocker.call(
                parent=mock_direct_frame,
                text=f"{info['LapNumber']:.0f}",
                align=TextNode.ACenter,
                scale=11,
                font=driver_window.app.text_font,
                fg=Colors.HIGHLIGHTER_YELLOW,
                pos=(end, driver_window.tire_strategy_height - title_frame_height - 50, 0),
            ),
        )

    expected_onscreen_text_calls.append(
        mocker.call(
            parent=mock_direct_frame,
            text="1",
            align=TextNode.ACenter,
            scale=11,
            font=driver_window.app.text_font,
            fg=Colors.HIGHLIGHTER_YELLOW,
            pos=(10, driver_window.tire_strategy_height - title_frame_height - 50, 0),
        ),
    )

    mock_onscreen_text_class.assert_has_calls(expected_onscreen_text_calls)


@pytest.mark.parametrize(
    ("indicator", "gear", "expected_color"),
    [
        ("N", "N", (102 / 255, 217 / 255, 126 / 255, 1)),
        ("1", "1", (102 / 255, 217 / 255, 126 / 255, 1)),
        ("1", "2", (0.7, 0.7, 0.7, 1)),
        ("5", "3", (0.7, 0.7, 0.7, 1)),
        ("8", "8", (102 / 255, 217 / 255, 126 / 255, 1)),
    ],
)
def test_update_gear_indicator_updates_color_when_current_differs(
    driver_window: DriverWindow,
    mocker: MockerFixture,
    indicator: str,
    gear: str,
    expected_color: tuple[float, float, float, float],
) -> None:
    mock_indicator_text = mocker.MagicMock(spec=OnscreenText)
    mock_text_node = mocker.MagicMock()
    mock_text_node.getTextColor.return_value = (1, 1, 1, 1)
    mock_indicator_text.textNode = mock_text_node

    setattr(driver_window, f"gear_{indicator}", mock_indicator_text)

    driver_window.update_gear_indicator(indicator, gear)

    mock_indicator_text.__setitem__.assert_called_once_with("fg", expected_color)


def test_update_gear_indicator_does_not_update_when_color_same(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    green_color = (102 / 255, 217 / 255, 126 / 255, 1)

    mock_indicator_text = mocker.MagicMock(spec=OnscreenText)
    mock_text_node = mocker.MagicMock()
    mock_text_node.getTextColor.return_value = green_color
    mock_indicator_text.textNode = mock_text_node

    driver_window.gear_1 = mock_indicator_text

    driver_window.update_gear_indicator("1", "1")

    mock_indicator_text.__setitem__.assert_not_called()


@pytest.mark.parametrize(
    ("drs", "expected_color"),
    [
        (0, Colors.GRAY),
        (1,  Colors.LIGHT_RED),
        (14, Colors.GREEN),
    ],
)
def test_update_drs_indicator_updates_color_when_current_differs(
    driver_window: DriverWindow,
    mocker: MockerFixture,
    drs: int,
    expected_color: tuple[float, float, float, float],
) -> None:
    mock_drs_text = mocker.MagicMock(spec=OnscreenText)
    mock_text_node = mocker.MagicMock()
    mock_text_node.getTextColor.return_value = (1, 1, 1, 1)
    mock_drs_text.textNode = mock_text_node

    driver_window.drs = mock_drs_text

    driver_window.update_drs_indicator(drs)

    mock_drs_text.__setitem__.assert_called_once_with("fg", expected_color)


def test_update_drs_indicator_does_not_update_when_color_same(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_drs_text = mocker.MagicMock(spec=OnscreenText)
    mock_text_node = mocker.MagicMock()
    mock_text_node.getTextColor.return_value = Colors.GRAY
    mock_drs_text.textNode = mock_text_node

    driver_window.drs = mock_drs_text

    driver_window.update_drs_indicator(0)

    mock_drs_text.__setitem__.assert_not_called()


@pytest.mark.parametrize(
    ("gear", "rpm", "brake", "speed_kph", "drs", "speed_mph", "throttle"),
    [
        ("N", 1000.0, True, 16.0, 0, 10.0, 100.0),
        ("1", 5000.0, True, 50.0, 0, 31.0, 75.0),
        ("3", 10000.0, True, 150.0, 1, 93.0, 100.0),
        ("8", 15000.0, True, 330.0, 14, 205.0, 100.0),
    ],
)
def test_update_telemetry_updates_all_components(
    driver_window: DriverWindow,
    mocker: MockerFixture,
    gear: str,
    rpm: float,
    brake: bool,
    speed_kph: float,
    drs: int,
    speed_mph: float,
    throttle: float,
) -> None:
    mock_update_gear = mocker.patch.object(driver_window, "update_gear_indicator")
    mock_update_rpm = mocker.patch.object(driver_window, "update_drs_indicator")
    mock_speed_kph_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_kph_text.text = "0"
    mock_drs_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_mph_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_mph_text.text = "0"
    mock_rpm_frame = mocker.MagicMock(spec=DirectFrame)
    mock_rpm_frame.__getitem__ = mocker.MagicMock(return_value=(0, 0, 0, 10))
    mock_brake_frame = mocker.MagicMock(spec=DirectFrame)
    mock_brake_frame.__getitem__ = mocker.MagicMock(return_value=(-10, 10, 0, 0))
    mock_throttle_frame = mocker.MagicMock(spec=DirectFrame)
    mock_throttle_frame.__getitem__ = mocker.MagicMock(return_value=(-10, 10, 0, 0))

    driver_window.speed_kph = mock_speed_kph_text
    driver_window.drs = mock_drs_text
    driver_window.speed_mph = mock_speed_mph_text
    driver_window.rpm = mock_rpm_frame
    driver_window.brake = mock_brake_frame
    driver_window.throttle = mock_throttle_frame

    driver_window.update_telemetry(gear, rpm, brake, speed_kph, drs, speed_mph, throttle)

    mock_update_gear.assert_has_calls([
        mocker.call(indicator, gear) for indicator in ["N", "1", "2", "3", "4", "5", "6", "7", "8"]
    ])
    mock_update_rpm.assert_called_once_with(drs)
    mock_speed_kph_text.__setitem__.assert_called_with("text", f"{speed_kph:.0f}")
    mock_speed_mph_text.__setitem__.assert_called_with("text", f"{speed_mph:.0f}")
    mock_rpm_frame.__setitem__.assert_called_with("frameSize", (0, rpm / 15000 * 240, 0, 10))
    mock_brake_frame.__setitem__.assert_called_with("frameSize", (-10, 10, 0, 100 if brake else 0))
    mock_throttle_frame.__setitem__.assert_called_with("frameSize", (-10, 10, 0, throttle))


def test_update_telemetry_skips_updates_when_values_unchanged(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    gear = "3"
    rpm = 10000.0
    drs = 1
    speed_kph = 150.0
    speed_mph = 93.0
    throttle = 75.0

    mock_update_gear = mocker.patch.object(driver_window, "update_gear_indicator")
    mock_update_drs = mocker.patch.object(driver_window, "update_drs_indicator")
    mock_speed_kph_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_kph_text.text = f"{speed_kph:.0f}"
    mock_drs_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_mph_text = mocker.MagicMock(spec=OnscreenText)
    mock_speed_mph_text.text = f"{speed_mph:.0f}"
    mock_rpm_frame = mocker.MagicMock(spec=DirectFrame)
    mock_rpm_frame.__getitem__ = mocker.MagicMock(return_value=(0, rpm / 15000 * 240, 0, 10))
    mock_brake_frame = mocker.MagicMock(spec=DirectFrame)
    mock_brake_frame.__getitem__ = mocker.MagicMock(return_value=(-10, 10, 0, 0))
    mock_throttle_frame = mocker.MagicMock(spec=DirectFrame)
    mock_throttle_frame.__getitem__ = mocker.MagicMock(return_value=(-10, 10, 0, throttle))

    driver_window.speed_kph = mock_speed_kph_text
    driver_window.drs = mock_drs_text
    driver_window.speed_mph = mock_speed_mph_text
    driver_window.rpm = mock_rpm_frame
    driver_window.brake = mock_brake_frame
    driver_window.throttle = mock_throttle_frame

    driver_window.update_telemetry(gear, rpm, False, speed_kph, drs, speed_mph, throttle)

    mock_update_gear.assert_has_calls([
        mocker.call(indicator, gear) for indicator in ["N", "1", "2", "3", "4", "5", "6", "7", "8"]
    ])
    mock_update_drs.assert_called_once_with(drs)
    mock_speed_kph_text.__setitem__.assert_not_called()
    mock_speed_mph_text.__setitem__.assert_not_called()
    mock_rpm_frame.__setitem__.assert_not_called()
    mock_brake_frame.__setitem__.assert_not_called()
    mock_throttle_frame.__setitem__.assert_not_called()


def test_update_camera_position_sets_camera_position_and_looks_at(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    from decimal import Decimal

    x = Decimal("10.123")
    y = Decimal("20.456")
    z = Decimal("30.789")

    mock_camera_np = mocker.MagicMock(spec=NodePath)
    driver_window._camera_np = mock_camera_np

    driver_window.update_camera_position(x, y, z)

    mock_camera_np.setX.assert_called_once_with(x + 5)
    mock_camera_np.setY.assert_called_once_with(y + 5)
    mock_camera_np.setZ.assert_called_once_with(z + 5)
    mock_camera_np.lookAt.assert_called_once_with(x, y, z)


def test_update(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    from decimal import Decimal

    mock_update_telemetry = mocker.patch.object(driver_window, "update_telemetry")
    mock_update_camera = mocker.patch.object(driver_window, "update_camera_position")
    mock_update_lap_time_line = mocker.patch.object(driver_window, "update_lap_time_line")
    mock_update_current_lap = mocker.patch.object(driver_window, "update_current_lap")

    current_record = {
        "PositionIndex": 2,
        "LapNumber": 15,
        "TotalLaps": 60.0,
        "nGear": "3",
        "RPM": 10000.0,
        "Brake": True,
        "Speed": 150.0,
        "DRS": 0.0,
        "SpeedMph": 93.0,
        "Throttle": 75.0,
        "X": "10.123",
        "Y": "20.456",
        "Z": "30.789",
        "LapsCompletion": 14.23,
    }

    driver_window.update(current_record)

    mock_update_telemetry.assert_called_once_with("3", 10000.0, True, 150.0, 0, 93.0, 75.0)
    mock_update_camera.assert_called_once_with(
        Decimal("10.123"),
        Decimal("20.456"),
        Decimal("30.789"),
    )
    mock_update_lap_time_line.assert_called_once_with(current_record["LapsCompletion"])
    mock_update_current_lap.assert_called_once_with(current_record)


def test_open_calls_make_widgets_and_sets_is_open_true(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_make_driver = mocker.patch.object(driver_window, "make_driver_widget")
    mock_make_camera = mocker.patch.object(driver_window, "make_camera_region")
    mock_make_telemetry = mocker.patch.object(driver_window, "make_telemetry_widget")
    mock_make_strategy = mocker.patch.object(driver_window, "make_tire_strategy_widget")
    mock_make_lap_widget = mocker.patch.object(driver_window, "make_lap_widget")
    mock_make_laps_widget = mocker.patch.object(driver_window, "make_laps_widget")

    driver_window.open()

    assert driver_window.is_open is True
    mock_make_driver.assert_called_once()
    mock_make_camera.assert_called_once()
    mock_make_telemetry.assert_called_once()
    mock_make_strategy.assert_called_once()
    mock_make_lap_widget.assert_called_once()
    mock_make_laps_widget.assert_called_once()


def test_open_returns_early_if_already_open(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_make_driver = mocker.patch.object(driver_window, "make_driver_widget")
    mock_make_camera = mocker.patch.object(driver_window, "make_camera_region")
    mock_make_telemetry = mocker.patch.object(driver_window, "make_telemetry_widget")
    mock_make_strategy = mocker.patch.object(driver_window, "make_tire_strategy_widget")
    mock_make_lap_widget = mocker.patch.object(driver_window, "make_lap_widget")
    mock_make_laps_widget = mocker.patch.object(driver_window, "make_laps_widget")

    driver_window.is_open = True

    driver_window.open()

    assert driver_window.is_open is True
    mock_make_driver.assert_not_called()
    mock_make_camera.assert_not_called()
    mock_make_telemetry.assert_not_called()
    mock_make_strategy.assert_not_called()
    mock_make_lap_widget.assert_not_called()
    mock_make_laps_widget.assert_not_called()


def test_close(
    driver_window: DriverWindow,
    mocker: MockerFixture,
) -> None:
    mock_window = mocker.MagicMock(spec=GraphicsWindow)
    mock_render2d = mocker.MagicMock(spec=NodePath)
    mock_app = driver_window.app

    driver_window._window = mock_window
    driver_window._render2d = mock_render2d
    driver_window.is_open = True

    driver_window.close()

    assert driver_window.is_open is False
    mock_window.removeAllDisplayRegions.assert_called_once()
    mock_render2d.removeNode.assert_called_once()
    mock_app.closeWindow.assert_called_once_with(mock_window)

    assert driver_window._window is None
    assert driver_window._render2d is None
    assert driver_window._pixel2d is None
    assert driver_window._lens is None
    assert driver_window._camera is None
    assert driver_window._camera_np is None
