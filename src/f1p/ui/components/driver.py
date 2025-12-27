from dataclasses import dataclass
from datetime import timedelta
from unittest import case

import numpy
import numpy as np
import pandas as pd
from fastf1.core import Lap
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

    current_lap: Lap | None = None

    node_path: NodePath = None

    @property
    def team_color_obj(self) -> LVecBase4f:
        return self.node_path.getColor()

    @property
    def current_lap_number(self) -> int:
        return int(self.current_lap.iloc[0]["LapNumber"])

    @property
    def current_position(self) -> int:
        position = self.current_lap.iloc[0]["Position"]

        if pd.isna(position):
            return 99

        return int(position)

    def is_in_pit(self, session_time: timedelta) -> bool:
        in_time = self.current_lap.iloc[0]["PitInTime"]
        out_time = self.current_lap.iloc[0]["PitOutTime"]

        if pd.notna(in_time):
            return in_time <= session_time

        if pd.notna(out_time):
            return session_time <= out_time

        return False

    @property
    def current_tire_compound_color(self) -> tuple[float, float, float, float]:
        match self.current_tire_compound:
            case "S":
                return 1, 0, 0, 0.8
            case "M":
                return 1, 1, 0, 0.8
            case "H":
                return 1, 1, 1, 0.8
            case "I":
                return 0, 1, 0, 0.8
            case "W":
                return 0, 0, 1, 0.8
            case _:
                return 0, 0, 0, 0.8

    @property
    def current_tire_compound(self) -> str:
        compound = self.current_lap.iloc[0]["Compound"]

        return compound[0]

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

    def update_coordinates(self, session_time: timedelta) -> None:
        pos_data_passed = self.pos_data[self.pos_data["SessionTime"] <= session_time]
        current_record = pos_data_passed.tail(1)

        X = current_record["X"].item()
        Y = current_record["Y"].item()
        Z = current_record["Z"].item()

        self.node_path.setPos(X, Y, Z)
