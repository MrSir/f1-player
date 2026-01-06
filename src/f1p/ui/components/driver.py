from decimal import Decimal

from direct.showbase.DirectObject import DirectObject
from fastf1.core import Lap, Telemetry, Laps
from panda3d.core import NodePath, LVecBase4f
from pandas import Series, Timedelta

from f1p.services.procedural3d import SphereMaker
from f1p.utils.color import hex_to_rgb_saturation


class Driver(DirectObject):
    def __init__(
        self,
        number: str,
        first_name: str,
        last_name: str,
        broadcast_name: str,
        abbreviation: str,
        team_name: str,
        team_color: str,
        pos_data: Telemetry,
        current_lap: Lap | None = None,
        current_lap_time: Timedelta = Timedelta(milliseconds=0),
        time_to_car_in_front: Timedelta = Timedelta(milliseconds=0),
        time_to_leader: Timedelta = Timedelta(milliseconds=0),
        node_path: NodePath = None,
        laps: Laps | None = None,
    ):
        super().__init__()

        self.number = number
        self.first_name = first_name
        self.last_name = last_name
        self.broadcast_name = broadcast_name
        self.abbreviation = abbreviation
        self.team_name = team_name
        self.team_color = team_color
        self.pos_data = pos_data
        self.ticks = self.pos_data.set_index("SessionTimeTick").to_dict(orient='index')
        self.current_lap = current_lap
        self.current_lap_time = current_lap_time
        self.time_to_car_in_front = time_to_car_in_front
        self.time_to_leader = time_to_leader
        self.node_path = node_path
        self.laps = laps
        self.in_pit: bool = False
        self.is_dnf: bool = False
        self.is_finished: bool = False
        self.has_fastest_lap: bool = False

        self.accept("updateDrivers", self.update)

        self._last_session_time: int | None = None

    @property
    def team_color_obj(self) -> LVecBase4f:
        return self.node_path.getColor()

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
    def from_df(
        cls,
        parent: NodePath,
        driver_sr: Series,
        pos_data: Telemetry,
        laps: Laps,
    ) -> Driver:
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
            laps=laps,
        )

    def update(self, session_time_tick: int) -> None:
        current_record = self.ticks[session_time_tick]

        self.is_dnf = current_record["IsDNF"]
        self.in_pit = current_record["InPit"]
        self.is_finished = current_record["IsFinished"]
        self.has_fastest_lap = current_record["HasFastestLap"]

        precision = Decimal("0.001")

        X = Decimal(current_record["X"]).quantize(precision)
        Y = Decimal(current_record["Y"]).quantize(precision)
        Z = Decimal(current_record["Z"]).quantize(precision)

        current_pos = self.node_path.getPos()
        current_X = Decimal(current_pos.x).quantize(precision)
        current_Y = Decimal(current_pos.y).quantize(precision)
        current_Z = Decimal(current_pos.z).quantize(precision)

        if (current_X, current_Y, current_Z) != (X, Y, Z):
            self.node_path.setPos(X, Y, Z)
