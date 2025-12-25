from dataclasses import dataclass

from panda3d.core import GeomNode, NodePath, LVecBase4f, VBase4F
from pandas import Series, DataFrame

from f1p.services.procedural3d import SphereMaker
from f1p.utils.color import hex_to_rgb_saturation


@dataclass
class Driver:
    number: str
    first_name: str
    last_name: str
    broadcast_name: str
    abbreviation: str
    team_name: str
    team_color: str

    pos_data: Series

    node_path: NodePath = None

    @staticmethod
    def create_node_path(parent, driver_sr: Series) -> NodePath:
        sphere_maker = SphereMaker(
            radius=0.10,
        )
        sphere = sphere_maker.generate()
        node_path = parent.attachNewNode(sphere)
        team_color_hex = driver_sr["TeamColor"]
        color = hex_to_rgb_saturation(f"#{team_color_hex}")
        node_path.setColor(
            color["rgb"][0] / 255,
            color["rgb"][1] / 255,
            color["rgb"][2] / 255,
            color["saturation_hls"],
        )

        return node_path

    @classmethod
    def from_df(cls, parent: NodePath, driver_sr: Series, pos_data: Series) -> Driver:
        return Driver(
            number=driver_sr["DriverNumber"],
            first_name=driver_sr["FirstName"],
            last_name=driver_sr["LastName"],
            broadcast_name=driver_sr["BroadcastName"],
            abbreviation=driver_sr["Abbreviation"],
            team_name=driver_sr["TeamName"],
            team_color=driver_sr["TeamColor"],
            pos_data=pos_data,
            node_path=cls.create_node_path(parent, driver_sr),
        )

    def update_coordinates(self, driver_df: DataFrame) -> None:
        X = driver_df["X"].item()
        Y = driver_df["Y"].item()
        Z = driver_df["Z"].item()

        self.node_path.setPos(X, Y, Z)
