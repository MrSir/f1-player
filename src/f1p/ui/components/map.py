from typing import Any

import numpy as np
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task, TaskManager
from panda3d.core import BillboardEffect, LineSegs, NodePath, TextNode
from pandas import DataFrame

from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.driver import Driver


class Map(DirectObject):
    def __init__(self, parent: NodePath, task_manager: TaskManager, data_extractor: DataExtractorService):
        super().__init__()

        self.parent = parent
        self.task_manager = task_manager
        self.data_extractor = data_extractor

        self.inner_border_node_path: NodePath | None = None
        self.outer_border_node_path: NodePath | None = None

        self.drivers: list[Driver] = []
        self._pos_data: DataFrame | None = None
        self._map_center_coordinate: list[float] | None = None

        self.accept("sessionSelected", self.render_task)

    def render_map(self) -> None:
        new_df = self.data_extractor.fastest_lap_telemetry.copy()

        track_width = 0.5
        track_x = new_df["X"]
        track_y = new_df["Y"]

        dx = np.gradient(track_x)
        dy = np.gradient(track_y)

        norm = np.sqrt(dx**2 + dy**2)
        norm[norm == 0] = 10
        dx /= norm
        dy /= norm

        nx = -dy
        ny = dx
        x_outer = track_x + nx * (track_width / 2)
        y_outer = track_y + ny * (track_width / 2)
        x_inner = track_x - nx * (track_width / 2)
        y_inner = track_y - ny * (track_width / 2)

        inner_df = new_df.copy()
        inner_df["X"] = x_inner
        inner_df["Y"] = y_inner
        inner_track = inner_df.loc[:, ("X", "Y", "Z")].to_numpy().tolist()
        self.inner_border_node_path = self.draw_track(inner_track, (0.9, 0.9, 0.9, 1))
        self.inner_border_node_path.reparentTo(self.parent)

        outer_df = new_df.copy()
        outer_df["X"] = x_outer
        outer_df["Y"] = y_outer
        outer_track = outer_df.loc[:, ("X", "Y", "Z")].to_numpy().tolist()
        self.outer_border_node_path = self.draw_track(outer_track, (0.9, 0.9, 0.9, 1))
        self.outer_border_node_path.reparentTo(self.parent)

    def draw_track(self, track: list[list[float]], color: tuple[float, float, float, float]):
        line_segments = LineSegs("map")
        line_segments.setThickness(1)
        line_segments.setColor(*color)

        first_point = None
        previous_point = None
        for point in track:
            if first_point is None:
                first_point = point

            if previous_point is not None:
                line_segments.drawTo(point[0], point[1], point[2])

            previous_point = point
            line_segments.moveTo(previous_point[0], previous_point[1], previous_point[2])

        line_segments.drawTo(first_point[0], first_point[1], first_point[2])

        line_node = line_segments.create(False)

        return NodePath(line_node)

    def render_corners(self) -> None:
        line_segments = LineSegs("corners")
        line_segments.setThickness(1)
        line_segments.setColor(1, 1, 1, 0.5)

        for corner in self.data_extractor.processed_corners.itertuples():
            line_segments.moveTo(corner.X, corner.Y, self.data_extractor.lowest_z_coordinate)
            line_segments.drawTo(corner.X, corner.Y, corner.Z)

            turn = TextNode(f"turn{corner.Label}")
            turn.setText(corner.Label)
            turn.setAlign(TextNode.ACenter)
            turn.setTextScale(0.7)
            turn.setTextColor(0.8, 1, 0, 0.7)

            turn_np = self.parent.attachNewNode(turn)
            turn_np.setPos(corner.X, corner.Y, corner.Z)
            turn.setCardDecal(True)
            turn_np.setEffect(BillboardEffect.makePointEye())

        line_node = line_segments.create(False)
        node_path = NodePath(line_node)
        node_path.reparentTo(self.parent)

    def initialize_drivers(self) -> None:
        for _, driver_sr in self.data_extractor.session_results.iterrows():
            driver_pos_data = self.data_extractor.processed_pos_data[
                self.data_extractor.processed_pos_data["DriverNumber"] == driver_sr["DriverNumber"]
            ]

            self.drivers.append(Driver.from_df(self.parent, driver_sr, driver_pos_data))

    def render_task(self) -> None:
        self.task_manager.add(self.render, "renderMap")

    def render(self, task: Task) -> Any:
        self.render_map()
        self.render_corners()
        self.initialize_drivers()

        return task.done
