import numpy as np
from direct.showbase.DirectObject import DirectObject
from fastf1.core import Telemetry
from fastf1.mvapi import CircuitInfo
from panda3d.core import LineSegs, NodePath, deg2Rad
from pandas import DataFrame

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver
from f1p.utils.geometry import rotate, scale, shift, find_center


class Map(DirectObject):
    def __init__(self, parent: NodePath, data_extractor: DataExtractorService):
        super().__init__()

        self.parent = parent
        self.data_extractor = data_extractor

        self.inner_border_node_path: NodePath | None = None
        self.outer_border_node_path: NodePath | None = None

        self.drivers: list[Driver] = []
        self._pos_data: DataFrame | None = None
        self._map_center_coordinate: list[float] | None = None

        self.accept("sessionSelected", self.select_session)
        self.accept("clearMaps", self.clear_out_maps)

    @property
    def circuit_info(self) -> CircuitInfo:
        return self.data_extractor.circuit_info

    @property
    def map_rotation(self) -> float:
        return deg2Rad(self.circuit_info.rotation)

    @property
    def fastest_lap_telemetry(self) -> Telemetry:
        return self.data_extractor.fastest_lap.get_pos_data()

    def transform_coordinates(self, coordinates_df: Telemetry) -> DataFrame:
        new_coordinates_df = coordinates_df.copy()
        coordinates_cols_only_df = new_coordinates_df[['X', 'Y', 'Z']]

        rotated_coordinates_df = rotate(coordinates_cols_only_df, self.map_rotation)
        scaled_coordinates_df = scale(rotated_coordinates_df, 1 / 600)

        if self._map_center_coordinate is None:
            self._map_center_coordinate = find_center(scaled_coordinates_df)

        shifted_x_coordinates_df = shift(scaled_coordinates_df, direction="X", amount=-self._map_center_coordinate[0])
        shifted_y_coordinates_df = shift(scaled_coordinates_df, direction="Y", amount=-self._map_center_coordinate[1])
        shifted_z_coordinates_df = shift(scaled_coordinates_df, direction="Z", amount=-self._map_center_coordinate[2])

        new_coordinates_df["X"] = shifted_x_coordinates_df["X"]
        new_coordinates_df["Y"] = shifted_y_coordinates_df["Y"]
        new_coordinates_df["Z"] = shifted_z_coordinates_df["Z"]

        return new_coordinates_df

    def render_map(self, df: DataFrame) -> None:
        new_df = df.copy()

        track_width = 0.5
        track_x = new_df["X"]
        track_y = new_df["Y"]

        dx = np.gradient(track_x)
        dy = np.gradient(track_y)

        norm = np.sqrt(dx ** 2 + dy ** 2)
        norm[norm == 0] = 1.0
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
        inner_track = inner_df.loc[:, ('X', 'Y', 'Z')].to_numpy()
        self.inner_border_node_path = self.draw_track(inner_track, (0.9, 0.9, 0.9, 1))
        self.inner_border_node_path.reparentTo(self.parent)

        outer_df = new_df.copy()
        outer_df["X"] = x_outer
        outer_df["Y"] = y_outer
        outer_track = outer_df.loc[:, ('X', 'Y', 'Z')].to_numpy()
        self.outer_border_node_path = self.draw_track(outer_track, (0.9, 0.9, 0.9, 1))
        self.outer_border_node_path.reparentTo(self.parent)

    def draw_track(self, track: list[tuple[float, float, float]], color: tuple[float, float, float, float]):
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

    def clear_out_maps(self) -> None:
        if self.inner_border_node_path is not None:
            self.inner_border_node_path.removeNode()

        if self.outer_border_node_path is not None:
            self.outer_border_node_path.removeNode()

    @property
    def adjusted_pos_data(self) -> DataFrame:
        if self._pos_data is None:
            pos_data = self.data_extractor.session.pos_data

            for _, driver_sr in self.data_extractor.session.results.iterrows():
                driver_pos_data = pos_data[driver_sr["DriverNumber"]]
                transformed_pos_data = self.transform_coordinates(driver_pos_data)
                pos_data[driver_sr["DriverNumber"]] = transformed_pos_data

            self._pos_data = pos_data

        return self._pos_data

    def initialize_drivers(self) -> None:
        for _, driver_sr in self.data_extractor.session.results.iterrows():
            driver = Driver.from_df(self.parent, driver_sr, self.adjusted_pos_data[driver_sr["DriverNumber"]])

            self.drivers.append(driver)

    def select_session(self) -> None:
        self.render_map(self.transform_coordinates(self.fastest_lap_telemetry))
        self.initialize_drivers()
