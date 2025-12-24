from dataclasses import dataclass

from fastf1.core import Telemetry
from pandas import DataFrame, Series


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

    X: float = None
    Y: float = None
    Z: float = None

    @classmethod
    def from_df(cls, driver_sr: Series, pos_data: Series) -> Driver:
        return Driver(
            number=driver_sr["DriverNumber"],
            first_name=driver_sr["FirstName"],
            last_name=driver_sr["LastName"],
            broadcast_name=driver_sr["BroadcastName"],
            abbreviation=driver_sr["Abbreviation"],
            team_name=driver_sr["TeamName"],
            team_color=driver_sr["TeamColor"],
            pos_data=pos_data,
        )

