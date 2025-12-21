from direct.showbase.DirectObject import DirectObject
from fastf1.core import Telemetry
from fastf1.mvapi import CircuitInfo
from panda3d.core import LineSegs, NodePath
from pandas import DataFrame

from f1p.services.data_extractor import DataExtractorService


class Map(DirectObject):
    def __init__(self, parent: NodePath,  data_extractor: DataExtractorService):
        super().__init__()

        self.parent = parent
        self.data_extractor = data_extractor

        self.fastest_lap_node_path: NodePath | None = None
        self.outer_border_node_path: NodePath | None = None

        self.accept("sessionSelected", self.render)
        self.accept("clearMaps", self.clear_out_maps)

    @property
    def circuit_info(self) -> CircuitInfo:
        return self.data_extractor.circuit_info

    @property
    def fastest_lap_telemetry(self) -> Telemetry:
        return self.data_extractor.fastest_lap.get_pos_data()

    def scale(self, df: DataFrame, factor: float) -> DataFrame:
        new_df = df.copy()
        new_df["X"] = new_df["X"] * factor
        new_df["Y"] = new_df["Y"] * factor
        new_df["Z"] = new_df["Z"] * factor

        return new_df

    def shift(self, df: DataFrame, direction: str, amount: float) -> DataFrame:
        new_df = df.copy()
        new_df[direction] = new_df[direction] + amount

        return new_df

    def df_center(self, df: DataFrame) -> list[float]:
        return [
            ((df["X"].max() - df["X"].min()) / 2) + df["X"].min(),
            ((df["Y"].max() - df["Y"].min()) / 2) + df["Y"].min(),
            ((df["Z"].max() - df["Z"].min()) / 2) + df["Z"].min(),
        ]

    def render_map(self, df: DataFrame) -> NodePath:
        line_segments = LineSegs("map")
        line_segments.setThickness(3)
        line_segments.setColor(1, 0, 0, 1)

        track = df.loc[:, ('X', 'Y', 'Z')].to_numpy()

        first_point  = None
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
        fastest_lap_telemetry = self.fastest_lap_telemetry
        coordinates_only = fastest_lap_telemetry[['X', 'Y', 'Z']]
        scaled_coordinates_df = self.scale(coordinates_only, 1/600)

        df_center = self.df_center(scaled_coordinates_df)

        shifted_x_coordinates_df = self.shift(scaled_coordinates_df, direction="X", amount=-df_center[0])
        shifted_y_coordinates_df = self.shift(shifted_x_coordinates_df, direction="Y", amount=-df_center[1])
        shifted_z_coordinates_df = self.shift(shifted_y_coordinates_df, direction="Z", amount=-df_center[2])

        self.fastest_lap_node_path = self.render_map(shifted_z_coordinates_df)
        self.fastest_lap_node_path.reparentTo(self.parent)
