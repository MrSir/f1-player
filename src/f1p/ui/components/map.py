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

        self.fastest_lap_node_path: NodePath | None = None
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
    def fastest_lap_telemetry(self) -> Telemetry:
        return self.data_extractor.fastest_lap.get_pos_data()

    @property
    def scaled_map_coordinates(self):
        map_rotation = self.circuit_info.rotation
        map_rotation_rad = deg2Rad(map_rotation)

        fastest_lap_telemetry = self.fastest_lap_telemetry
        coordinates_only = fastest_lap_telemetry[['X', 'Y', 'Z']]

        rotated_coordinates = rotate(coordinates_only, map_rotation_rad)

        # TODO calculate scale factor such that maps are roughly same size
        return scale(rotated_coordinates, 1 / 600)


    @property
    def map_center_coordinate(self) -> list[float]:
        if self._map_center_coordinate is None:
            self._map_center_coordinate = find_center(self.scaled_map_coordinates)

        return self._map_center_coordinate

    def render_map(self, df: DataFrame) -> NodePath:
        line_segments = LineSegs("map")
        line_segments.setThickness(3)
        line_segments.setColor(1, 0, 0, 1)

        track = df.loc[:, ('X', 'Y', 'Z')].to_numpy()

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
        if self.fastest_lap_node_path is not None:
            self.fastest_lap_node_path.removeNode()

        if self.outer_border_node_path is not None:
            self.outer_border_node_path.removeNode()

    def render(self) -> None:
        # TODO calculate scale factor such that maps are roughly same size
        scaled_coordinates_df = self.scaled_map_coordinates

        df_center = self.map_center_coordinate

        shifted_x_coordinates_df = shift(scaled_coordinates_df, direction="X", amount=-df_center[0])
        shifted_y_coordinates_df = shift(shifted_x_coordinates_df, direction="Y", amount=-df_center[1])
        shifted_z_coordinates_df = shift(shifted_y_coordinates_df, direction="Z", amount=-df_center[2])

        self.fastest_lap_node_path = self.render_map(shifted_z_coordinates_df)
        self.fastest_lap_node_path.reparentTo(self.parent)

    @property
    def adjusted_pos_data(self) -> DataFrame:
        if self._pos_data is None:
            pos_data = self.data_extractor.session.pos_data
            map_rotation = self.circuit_info.rotation
            map_rotation_rad = deg2Rad(map_rotation)

            for _, driver_sr in self.data_extractor.session.results.iterrows():
                driver_pos_data = pos_data[driver_sr["DriverNumber"]]
                just_coordinates = driver_pos_data[['X', 'Y', 'Z']]
                rotated_coordinates = rotate(just_coordinates, map_rotation_rad)
                scaled_coordinates_df = scale(rotated_coordinates, 1 / 600)

                df_center = self.map_center_coordinate

                shifted_x_coordinates_df = shift(scaled_coordinates_df, direction="X", amount=-df_center[0])
                shifted_y_coordinates_df = shift(shifted_x_coordinates_df, direction="Y", amount=-df_center[1])
                shifted_z_coordinates_df = shift(shifted_y_coordinates_df, direction="Z", amount=-df_center[2])

                driver_pos_data["X"] = shifted_z_coordinates_df["X"]
                driver_pos_data["Y"] = shifted_z_coordinates_df["Y"]
                driver_pos_data["Z"] = shifted_z_coordinates_df["Z"]

                pos_data[driver_sr["DriverNumber"]] = driver_pos_data

            self._pos_data = pos_data

        return self._pos_data


    def initialize_drivers(self) -> None:
        # TODO rotate pos_data based on track angle
        for _, driver_sr in self.data_extractor.session.results.iterrows():
            driver = Driver.from_df(self.parent, driver_sr, self.adjusted_pos_data[driver_sr["DriverNumber"]])

            self.drivers.append(driver)

    def select_session(self) -> None:
        self.render()
        self.initialize_drivers()
