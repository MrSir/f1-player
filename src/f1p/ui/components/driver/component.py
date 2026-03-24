from decimal import Decimal
from typing import Any, Hashable

from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import LVecBase4f, NodePath
from pandas import DataFrame, Series

from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.driver.window import DriverWindow
from procedural3d import SphereMaker


class Driver(DirectObject):
    def __init__(
        self,
        app: ShowBase,
        number: str,
        first_name: str,
        last_name: str,
        broadcast_name: str,
        abbreviation: str,
        team_name: str,
        data_extractor: DataExtractorService,
        node_path: NodePath = None,
    ):
        super().__init__()

        self.app = app
        self.number = number
        self.first_name = first_name
        self.last_name = last_name
        self.broadcast_name = broadcast_name
        self.abbreviation = abbreviation
        self.team_name = team_name
        self.data_extractor = data_extractor
        self.node_path = node_path

        self._pos_data: DataFrame | None = None
        self._ticks: dict[Hashable, dict[Hashable, Any]] | None = None
        self._strategy: dict[int, dict[str, str | int]] | None = None
        self._driver_window: DriverWindow | None = None

        self.in_pit: bool = False
        self.is_dnf: bool = False
        self.is_finished: bool = False
        self.has_fastest_lap: bool = False


        self.accept("updateDrivers", self.queue_update)

    @property
    def pos_data(self) -> DataFrame:
        if self._pos_data is None:
            self._pos_data = self.data_extractor.processed_pos_data[
                self.data_extractor.processed_pos_data["DriverNumber"] == self.number
            ]

        return self._pos_data

    @property
    def ticks(self) -> dict[Hashable, dict[Hashable, Any]]:
        if self._ticks is None:
            self._ticks = self.pos_data.set_index("SessionTimeTick").to_dict(orient="index")

        return self._ticks

    @property
    def driver_window(self) -> DriverWindow:
        if self._driver_window is None:
            self._driver_window = DriverWindow(
                800,
                900,
                self.number,
                self.first_name,
                self.last_name,
                self.team_color_obj,
                self.team_name,
                self.app,
                self.data_extractor,
            )

        return self._driver_window

    @property
    def team_color_obj(self) -> LVecBase4f:
        return self.node_path.getColor()

    @staticmethod
    def create_node_path(parent: NodePath, team_color: tuple[float, float, float, float]) -> NodePath:
        sphere_maker = SphereMaker(
            radius=0.10,
        )
        sphere = sphere_maker.generate()
        node_path = parent.attachNewNode(sphere)
        node_path.setColor(*team_color)

        return node_path

    @classmethod
    def from_df(
        cls,
        app: ShowBase,
        parent: NodePath,
        data_extractor: DataExtractorService,
        driver_sr: Series,
    ) -> Driver:
        return Driver(
            app=app,
            number=driver_sr["DriverNumber"],
            first_name=driver_sr["FirstName"],
            last_name=driver_sr["LastName"],
            broadcast_name=driver_sr["BroadcastName"],
            abbreviation=driver_sr["Abbreviation"],
            team_name=driver_sr["TeamName"],
            data_extractor=data_extractor,
            node_path=cls.create_node_path(parent, driver_sr["TeamColor"]),
        )

    def queue_update(self, session_time_tick: int) -> None:
        self.app.taskMgr.add(
            self.update,
            "updateDriver",
            extraArgs=[session_time_tick],
            taskChain="updating",
        )

    def update(self, session_time_tick: int) -> None:
        current_record = self.ticks[session_time_tick]

        self.is_dnf = current_record["IsDNF"]
        self.in_pit = current_record["InPit"]
        self.is_finished = current_record["IsFinished"]
        self.has_fastest_lap = current_record["HasFastestLap"]

        precision = Decimal("0.001")

        x = Decimal(current_record["X"]).quantize(precision)
        y = Decimal(current_record["Y"]).quantize(precision)
        z = Decimal(current_record["Z"]).quantize(precision)

        current_pos = self.node_path.getPos()

        current_x = Decimal(current_pos.x).quantize(precision)
        current_y = Decimal(current_pos.y).quantize(precision)
        current_z = Decimal(current_pos.z).quantize(precision)

        if (current_x, current_y, current_z) != (x, y, z):
            self.node_path.setPos(x, y, z)

        if self.driver_window.is_open:
            self.driver_window.update(current_record)

    def open_driver(self) -> None:
        self.driver_window.open()

        driver_pos = self.node_path.getPos()
        self.driver_window.update_camera_position(driver_pos.x, driver_pos.y, driver_pos.z)
