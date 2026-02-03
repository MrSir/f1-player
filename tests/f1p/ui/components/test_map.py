from unittest.mock import MagicMock

import pytest
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task
from fastf1.core import Session
from panda3d.core import BillboardEffect, LineSegs, NodePath, TextNode
from pandas import DataFrame
from pytest_mock import MockerFixture

from f1p.ui.components.map import Map


@pytest.fixture()
def map_component(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_data_extractor: MagicMock,
    mocker: MockerFixture,
) -> Map:
    mock_accept = mocker.MagicMock()
    mocker.patch("f1p.ui.components.map.Map.accept", mock_accept)

    return Map(mock_parent, mock_task_manager, mock_data_extractor)


def test_initialization(
    mock_parent: MagicMock,
    mock_task_manager: MagicMock,
    mock_data_extractor: MagicMock,
    mocker: MockerFixture,
) -> None:
    mock_accept = mocker.MagicMock()
    mocker.patch("f1p.ui.components.map.Map.accept", mock_accept)

    map_component = Map(mock_parent, mock_task_manager, mock_data_extractor)

    assert isinstance(map_component, DirectObject)

    assert mock_parent == map_component.parent
    assert mock_task_manager == map_component.task_manager
    assert mock_data_extractor == map_component.data_extractor

    assert map_component.inner_border_node_path is None
    assert map_component.outer_border_node_path is None

    assert [] == map_component.drivers
    assert map_component._pos_data is None
    assert map_component._map_center_coordinate is None

    mock_accept.assert_called_once_with("sessionSelected", map_component.render_task)


def test_render_map(map_component: Map, mock_data_extractor: MagicMock, mocker: MockerFixture) -> None:
    telemetry_data = DataFrame({
        "X": [0.0, 1.0, 2.0, 3.0],
        "Y": [0.0, 1.0, 2.0, 3.0],
        "Z": [0.0, 0.0, 0.0, 0.0],
    })
    mock_data_extractor.fastest_lap_telemetry = telemetry_data

    mock_draw_track = mocker.MagicMock()
    mock_node_path = mocker.MagicMock(spec=NodePath)
    mock_draw_track.return_value = mock_node_path

    mocker.patch.object(map_component, "draw_track", mock_draw_track)

    map_component.render_map()

    outer_track = [
        [-0.17677669529663687, 0.17677669529663687, 0.0],
        [0.8232233047033631, 1.17677669529663687, 0.0],
        [1.8232233047033631, 2.17677669529663687, 0.0],
        [2.8232233047033631, 3.17677669529663687, 0.0],
    ]
    inner_track = [
        [0.17677669529663687, -0.17677669529663687, 0.0],
        [1.17677669529663687, 0.8232233047033631, 0.0],
        [2.17677669529663687, 1.8232233047033631, 0.0],
        [3.17677669529663687, 2.8232233047033631, 0.0],
    ]

    mock_draw_track.assert_has_calls(
        [
            mocker.call(inner_track, (0.9, 0.9, 0.9, 1)),
            mocker.call().reparentTo(map_component.parent),
            mocker.call(outer_track, (0.9, 0.9, 0.9, 1)),
            mocker.call().reparentTo(map_component.parent),
        ],
    )


def test_draw_track(map_component: Map, mocker: MockerFixture) -> None:
    mock_line_segs = mocker.MagicMock(spec=LineSegs)
    mock_line_node = mocker.MagicMock()
    mock_line_segs.create.return_value = mock_line_node
    mocker.patch("f1p.ui.components.map.LineSegs", return_value=mock_line_segs)

    mock_node_path = mocker.MagicMock(spec=NodePath)
    mocker.patch("f1p.ui.components.map.NodePath", return_value=mock_node_path)

    track = [
        [0.0, 0.0, 0.0],
        [1.0, 1.0, 0.0],
        [2.0, 2.0, 0.0],
    ]
    color = (1.0, 0.0, 0.0, 1.0)

    assert mock_node_path == map_component.draw_track(track, color)

    mock_line_segs.setThickness.assert_called_once_with(1)
    mock_line_segs.setColor.assert_called_with(*color)

    mock_line_segs.moveTo.assert_has_calls(
        [
            mocker.call(0.0, 0.0, 0.0),
            mocker.call(1.0, 1.0, 0.0),
            mocker.call(2.0, 2.0, 0.0),
        ],
    )
    mock_line_segs.drawTo.assert_has_calls(
        [
            mocker.call(1.0, 1.0, 0.0),
            mocker.call(2.0, 2.0, 0.0),
            mocker.call(0.0, 0.0, 0.0),
        ],
    )

    mock_line_segs.create.assert_called_once_with(False)


def test_render_corners(
    map_component: Map,
    mock_parent: MagicMock,
    mock_data_extractor: MagicMock,
    mocker: MockerFixture,
) -> None:
    corners_data = DataFrame({
        "X": [10.0, 20.0],
        "Y": [10.0, 20.0],
        "Z": [1.0, 1.0],
        "Label": ["1", "2"],
    })
    mock_data_extractor.processed_corners = corners_data
    mock_data_extractor.lowest_z_coordinate = 0.0

    mock_line_segs = mocker.MagicMock(spec=LineSegs)
    mock_line_node = mocker.MagicMock()
    mock_line_segs.create.return_value = mock_line_node
    mocker.patch("f1p.ui.components.map.LineSegs", return_value=mock_line_segs)

    mock_node_path_cls = mocker.patch("f1p.ui.components.map.NodePath")
    mock_node_path = mocker.MagicMock(spec=NodePath)
    mock_node_path_cls.return_value = mock_node_path

    mock_text_node = mocker.MagicMock(spec=TextNode)
    mock_text_node_class = mocker.MagicMock(return_value=mock_text_node)
    mocker.patch("f1p.ui.components.map.TextNode", mock_text_node_class)
    mock_billboard_effect = mocker.MagicMock(spec=BillboardEffect)
    mocker.patch("f1p.ui.components.map.BillboardEffect", mock_billboard_effect)

    map_component.render_corners()

    mock_line_segs.setThickness.assert_called_once_with(1)
    mock_line_segs.setColor.assert_called_with(1, 1, 1, 0.5)

    mock_line_segs.moveTo.assert_has_calls(
        [
            mocker.call(10.0, 10.0, 0.0),
            mocker.call(20.0, 20.0, 0.0),
        ],
    )
    mock_line_segs.drawTo.assert_has_calls(
        [
            mocker.call(10.0, 10.0, 1.0),
            mocker.call(20.0, 20.0, 1.0),
        ],
    )

    mock_parent.attachNewNode.assert_has_calls(
        [
            mocker.call(mock_text_node),
            mocker.call().setPos(10.0, 10.0, 1.0),
            mocker.call().setEffect(mock_billboard_effect.makePointEye.return_value),
            mocker.call(mock_text_node),
            mocker.call().setPos(20.0, 20.0, 1.0),
            mocker.call().setEffect(mock_billboard_effect.makePointEye.return_value),
        ],
    )

    mock_text_node_class.assert_has_calls(
        [
            mocker.call("turn1"),
            mocker.call("turn2"),
        ],
    )
    mock_text_node.setText.assert_has_calls(
        [
            mocker.call("1"),
            mocker.call("2"),
        ],
    )
    mock_text_node.setAlign.assert_has_calls(
        [
            mocker.call(mock_text_node_class.ACenter),
            mocker.call(mock_text_node_class.ACenter),
        ],
    )
    mock_text_node.setTextScale.assert_has_calls(
        [
            mocker.call(0.7),
            mocker.call(0.7),
        ],
    )
    mock_text_node.setTextColor.assert_has_calls(
        [
            mocker.call(0.8, 1, 0, 0.7),
            mocker.call(0.8, 1, 0, 0.7),
        ],
    )
    mock_text_node.setCardDecal.assert_has_calls(
        [
            mocker.call(True),
            mocker.call(True),
        ],
    )

    mock_line_segs.create.assert_called_once_with(False)
    mock_node_path_cls.assert_called_once_with(mock_line_node)
    mock_node_path.reparentTo.assert_called_once_with(map_component.parent)


def test_initialize_drivers(
    map_component: Map,
    mock_parent: MagicMock,
    mock_data_extractor: MagicMock,
    mocker: MockerFixture,
) -> None:
    driver_results = DataFrame({
        "DriverNumber": [1, 2],
        "FirstName": ["Lewis", "George"],
        "LastName": ["Hamilton", "Russell"],
        "BroadcastName": ["HAM", "RUS"],
        "Abbreviation": ["HAM", "RUS"],
        "TeamName": ["Team A", "Team B"],
        "TeamColor": [(1, 0, 0, 1), (0, 0, 1, 1)],
    })
    mock_data_extractor.session_results = driver_results

    pos_data = DataFrame({
        "SessionTimeTick": [1, 2, 1, 2],
        "DriverNumber": [1, 1, 2, 2],
        "X": [0.0, 1.0, 2.0, 3.0],
        "Y": [0.0, 1.0, 2.0, 3.0],
        "Z": [0.0, 0.0, 0.0, 0.0],
    })
    mock_data_extractor.processed_pos_data = pos_data

    map_component.initialize_drivers()

    assert len(map_component.drivers) == 2

    driver1_sr = driver_results.iloc[0]
    driver1_pos_data = pos_data[pos_data["DriverNumber"] == driver1_sr["DriverNumber"]]
    driver1 = map_component.drivers[0]
    assert isinstance(driver1, DirectObject)
    assert driver1_sr["DriverNumber"] == driver1.number
    assert driver1_sr["FirstName"] == driver1.first_name
    assert driver1_sr["LastName"] == driver1.last_name
    assert driver1_sr["BroadcastName"] == driver1.broadcast_name
    assert driver1_sr["Abbreviation"] == driver1.abbreviation
    assert driver1_sr["TeamName"] == driver1.team_name
    assert driver1_pos_data.equals(driver1.pos_data)
    assert driver1_pos_data.set_index("SessionTimeTick").to_dict(orient="index") == driver1.ticks
    assert mock_parent.attachNewNode.return_value == driver1.node_path
    assert driver1.in_pit is False
    assert driver1.is_dnf is False
    assert driver1.is_finished is False
    assert driver1.has_fastest_lap is False

    driver2_sr = driver_results.iloc[1]
    driver2_pos_data = pos_data[pos_data["DriverNumber"] == driver2_sr["DriverNumber"]]
    driver2 = map_component.drivers[1]
    assert isinstance(driver2, DirectObject)
    assert driver2_sr["DriverNumber"] == driver2.number
    assert driver2_sr["FirstName"] == driver2.first_name
    assert driver2_sr["LastName"] == driver2.last_name
    assert driver2_sr["BroadcastName"] == driver2.broadcast_name
    assert driver2_sr["Abbreviation"] == driver2.abbreviation
    assert driver2_sr["TeamName"] == driver2.team_name
    assert driver2_pos_data.equals(driver2.pos_data)
    assert driver2_pos_data.set_index("SessionTimeTick").to_dict(orient="index") == driver2.ticks
    assert mock_parent.attachNewNode.return_value == driver2.node_path
    assert driver2.in_pit is False
    assert driver2.is_dnf is False
    assert driver2.is_finished is False
    assert driver2.has_fastest_lap is False


def test_render_task(map_component: Map, mock_task_manager: MagicMock) -> None:
    map_component.render_task()

    mock_task_manager.add.assert_called_once_with(map_component.render, "renderMap")


def test_render(map_component: Map, mocker: MockerFixture) -> None:
    mock_render_map = mocker.MagicMock()
    mock_render_corners = mocker.MagicMock()
    mock_initialize_drivers = mocker.MagicMock()

    mocker.patch.object(map_component, "render_map", mock_render_map)
    mocker.patch.object(map_component, "render_corners", mock_render_corners)
    mocker.patch.object(map_component, "initialize_drivers", mock_initialize_drivers)

    mock_task = mocker.MagicMock(spec=Task)

    assert mock_task.done == map_component.render(mock_task)

    mock_render_map.assert_called_once()
    mock_render_corners.assert_called_once()
    mock_initialize_drivers.assert_called_once()
