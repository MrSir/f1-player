from decimal import Decimal
from unittest.mock import MagicMock

import pytest
from direct.showbase.DirectObject import DirectObject
from panda3d.core import LVecBase4f, NodePath
from pandas import DataFrame, Series
from pytest_mock import MockerFixture

from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.driver.component import Driver
from f1p.ui.components.driver.window import DriverWindow
from procedural3d import SphereMaker


@pytest.fixture
def ticks(pos_data: DataFrame) -> dict:
    return pos_data.set_index("SessionTimeTick").to_dict(orient="index")


@pytest.fixture
def driver_sr(session_results: DataFrame) -> Series:
    return session_results.iloc[0]


@pytest.fixture
def pos_data() -> DataFrame:
    return DataFrame(
        [
            {
                "SessionTimeTick": 1,
                "X": 1,
                "Y": 1,
                "Z": 1,
                "IsDNF": False,
                "InPit": False,
                "IsFinished": False,
                "HasFastestLap": False,
            },
            {
                "SessionTimeTick": 2,
                "X": 2,
                "Y": 2,
                "Z": 2,
                "IsDNF": True,
                "InPit": False,
                "IsFinished": False,
                "HasFastestLap": False,
            },
            {
                "SessionTimeTick": 3,
                "X": 3,
                "Y": 3,
                "Z": 3,
                "IsDNF": False,
                "InPit": True,
                "IsFinished": False,
                "HasFastestLap": False,
            },
            {
                "SessionTimeTick": 4,
                "X": 4,
                "Y": 4,
                "Z": 4,
                "IsDNF": False,
                "InPit": False,
                "IsFinished": True,
                "HasFastestLap": False,
            },
            {
                "SessionTimeTick": 5,
                "X": 5,
                "Y": 5,
                "Z": 5,
                "IsDNF": False,
                "InPit": False,
                "IsFinished": False,
                "HasFastestLap": True,
            },
        ],
    )


@pytest.fixture()
def strategy() -> dict[int, dict[str, str | int]]:
    return {
        1: {"Compound": "S", "CompoundColor": LVecBase4f(1, 0, 0, 0.8), "LapNumber": 10, "TotalLaps": 60},
        2: {"Compound": "M", "CompoundColor": LVecBase4f(1, 1, 0, 0.8), "LapNumber": 20, "TotalLaps": 60},
        3: {"Compound": "H", "CompoundColor": LVecBase4f(1, 1, 1, 0.8), "LapNumber": 30, "TotalLaps": 60},
    }


@pytest.fixture
def driver(
    mock_f1p_app: MagicMock,
    mock_parent: MagicMock,
    mock_data_extractor_service: MagicMock,
    driver_sr: Series,
) -> Driver:
    return Driver.from_df(mock_f1p_app, mock_parent, mock_data_extractor_service, driver_sr)


def test_initialization(
    mock_f1p_app: MagicMock,
    mock_data_extractor_service: MagicMock,
    mocker: MockerFixture,
) -> None:
    number = "1"
    first_name = "Joe"
    last_name = "Shmoe"
    broadcast_name = "JSH"
    abbreviation = "SHM"
    team_name = "Team 1"
    headshot_url = "https://some.img.url"

    mock_accept = mocker.MagicMock()
    mocker.patch("f1p.ui.components.driver.component.Driver.accept", mock_accept)

    driver = Driver(
        mock_f1p_app,
        number,
        first_name,
        last_name,
        broadcast_name,
        abbreviation,
        team_name,
        headshot_url,
        mock_data_extractor_service,
    )

    assert isinstance(driver, DirectObject)
    assert mock_f1p_app == driver.app
    assert number == driver.number
    assert first_name == driver.first_name
    assert last_name == driver.last_name
    assert broadcast_name == driver.broadcast_name
    assert abbreviation == driver.abbreviation
    assert team_name == driver.team_name
    assert headshot_url == driver.headshot_url
    assert mock_data_extractor_service == driver.data_extractor
    assert driver.node_path is None

    assert driver._pos_data is None
    assert driver._ticks is None
    assert driver._strategy is None
    assert driver._driver_window is None

    assert driver.in_pit is False
    assert driver.is_dnf is False
    assert driver.is_finished is False
    assert driver.has_fastest_lap is False

    mock_accept.assert_called_once_with("updateDrivers", driver.queue_update)


def test_driver_window_lazy_initialization(
    driver: Driver,
    mocker: MockerFixture,
) -> None:
    mock_driver_window = mocker.MagicMock(spec=DriverWindow)
    mock_driver_window_class = mocker.MagicMock(return_value=mock_driver_window)
    mocker.patch("f1p.ui.components.driver.component.DriverWindow", mock_driver_window_class)

    result = driver.driver_window

    assert mock_driver_window == result
    mock_driver_window_class.assert_called_once_with(
        800,
        900,
        driver.number,
        driver.first_name,
        driver.last_name,
        driver.team_color_obj,
        driver.team_name,
        driver.headshot_url,
        driver.app,
        driver.data_extractor,
    )


def test_driver_window_returns_cached_instance(
    driver: Driver,
    mocker: MockerFixture,
) -> None:
    mock_driver_window = mocker.MagicMock(spec=DriverWindow)
    mock_driver_window_class = mocker.MagicMock(return_value=mock_driver_window)
    mocker.patch("f1p.ui.components.driver.component.DriverWindow", mock_driver_window_class)

    result1 = driver.driver_window
    result2 = driver.driver_window

    assert result1 is result2
    mock_driver_window_class.assert_called_once()


def test_team_color_obj(driver: Driver, mocker: MockerFixture) -> None:
    color = LVecBase4f(1, 0, 0, 1)
    mock_node_path = mocker.MagicMock(space=NodePath)
    mock_node_path.getColor.return_value = color
    driver.node_path = mock_node_path

    assert color == driver.team_color_obj
    mock_node_path.getColor.assert_called_once()


def test_create_node_path(mock_parent: MagicMock, mocker: MockerFixture) -> None:
    sphere = mocker.MagicMock()
    mock_sphere_maker = mocker.MagicMock(spec=SphereMaker)
    mock_sphere_maker.generate.return_value = sphere
    mock_sphere_maker_class = mocker.MagicMock(return_value=mock_sphere_maker)
    mocker.patch("f1p.ui.components.driver.component.SphereMaker", mock_sphere_maker_class)

    node_path = mocker.MagicMock(spec=NodePath)
    mock_parent.attachNewNode.return_value = node_path

    color = (1, 0, 0, 1)

    assert node_path == Driver.create_node_path(mock_parent, color)
    mock_sphere_maker_class.assert_called_once_with(radius=0.10)
    mock_sphere_maker.generate.assert_called_once()
    mock_parent.attachNewNode.assert_called_once_with(sphere)
    node_path.setColor.assert_called_once_with(*color)


def test_from_df(
    mock_parent: MagicMock,
    driver_sr: Series,
    mock_f1p_app: MagicMock,
    mock_data_extractor_service: MagicMock,
) -> None:
    driver = Driver.from_df(mock_f1p_app, mock_parent, mock_data_extractor_service, driver_sr)

    assert isinstance(driver, DirectObject)
    assert mock_f1p_app == driver.app
    assert driver_sr["DriverNumber"] == driver.number
    assert driver_sr["FirstName"] == driver.first_name
    assert driver_sr["LastName"] == driver.last_name
    assert driver_sr["BroadcastName"] == driver.broadcast_name
    assert driver_sr["Abbreviation"] == driver.abbreviation
    assert driver_sr["TeamName"] == driver.team_name
    assert driver_sr["HeadshotUrl"] == driver.headshot_url
    assert mock_data_extractor_service == driver.data_extractor
    assert mock_parent.attachNewNode.return_value == driver.node_path

    assert driver._pos_data is None
    assert driver._ticks is None
    assert driver._strategy is None
    assert driver._driver_window is None

    assert driver.in_pit is False
    assert driver.is_dnf is False
    assert driver.is_finished is False
    assert driver.has_fastest_lap is False


def test_queue_update(driver: Driver, mock_f1p_app: MagicMock) -> None:
    session_time_tick = 2
    driver.queue_update(session_time_tick)

    mock_f1p_app.taskMgr.add.assert_called_once_with(
        driver.update,
        "updateDriver",
        extraArgs=[session_time_tick],
        taskChain="updating",
    )


@pytest.mark.parametrize(
    ("session_time_tick", "x", "y", "z", "is_dnf", "in_pit", "is_finished", "has_fastest_lap"),
    [
        (1, "1", "1", "1", False, False, False, False),
        (2, "2", "2", "2", True, False, False, False),
        (3, "3", "3", "3", False, True, False, False),
        (4, "4", "4", "4", False, False, True, False),
        (5, "5", "5", "5", False, False, False, True),
    ],
)
def test_update(
    session_time_tick: int,
    x: str,
    y: str,
    z: str,
    is_dnf: bool,
    in_pit: bool,
    is_finished: bool,
    has_fastest_lap: bool,
    driver: Driver,
    ticks: dict,
    mocker: MockerFixture,
) -> None:
    mock_pos = mocker.MagicMock()
    mock_pos.x = 1
    mock_pos.y = 1
    mock_pos.z = 1
    node_path = mocker.MagicMock(spec=NodePath)
    node_path.getPos.return_value = mock_pos
    driver.node_path = node_path
    driver._ticks = ticks

    driver.update(session_time_tick)

    assert is_dnf == driver.is_dnf
    assert in_pit == driver.in_pit
    assert is_finished == driver.is_finished
    assert has_fastest_lap == driver.has_fastest_lap

    node_path.getPos.assert_called_once()

    if session_time_tick > 1:
        precision = Decimal("0.001")
        parsed_x = Decimal(x).quantize(precision)
        parsed_y = Decimal(y).quantize(precision)
        parsed_z = Decimal(z).quantize(precision)
        node_path.setPos.assert_called_once_with(parsed_x, parsed_y, parsed_z)


def test_update_with_open_window(driver: Driver, ticks: dict, mocker: MockerFixture) -> None:
    mock_pos = mocker.MagicMock()
    mock_pos.x = 1
    mock_pos.y = 1
    mock_pos.z = 1
    node_path = mocker.MagicMock(spec=NodePath)
    node_path.getPos.return_value = mock_pos
    driver.node_path = node_path
    driver._ticks = ticks

    mock_driver_window = mocker.MagicMock(spec=DriverWindow)
    mock_driver_window.is_open = True
    driver._driver_window = mock_driver_window

    driver.update(2)

    assert driver.is_dnf is True
    assert driver.in_pit is False
    assert driver.is_finished is False
    assert driver.has_fastest_lap is False

    node_path.getPos.assert_called_once()
    precision = Decimal("0.001")
    parsed_x = Decimal(2).quantize(precision)
    parsed_y = Decimal(2).quantize(precision)
    parsed_z = Decimal(2).quantize(precision)
    node_path.setPos.assert_called_once_with(parsed_x, parsed_y, parsed_z)
    mock_driver_window.update.assert_called_once_with(driver.ticks[2])


def test_open_driver(driver: Driver, mocker: MockerFixture) -> None:
    mock_driver_window = mocker.MagicMock(spec=DriverWindow)
    driver._driver_window = mock_driver_window

    mock_node_path = mocker.MagicMock(spec=NodePath)
    mock_pos = mocker.MagicMock()
    mock_pos.x = 1.5
    mock_pos.y = 2.5
    mock_pos.z = 3.5
    mock_node_path.getPos.return_value = mock_pos
    driver.node_path = mock_node_path

    driver.open_driver()

    mock_driver_window.open.assert_called_once()
    mock_node_path.getPos.assert_called_once()
    mock_driver_window.update_camera_position.assert_called_once_with(1.5, 2.5, 3.5)
