from datetime import timedelta

import pandas as pd
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from fastf1.core import Laps
from panda3d.core import StaticTextFont, Point3, Loader, TransparencyAttrib, TextNode
from pandas import DataFrame, Timedelta

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver
from f1p.ui.components.gui.drop_down import BlackDropDown
from f1p.ui.components.map import Map


class Leaderboard(DirectObject):
    def __init__(
        self,
        pixel2d,
        render2d,
        task_manager: TaskManager,
        loader: Loader,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        circuit_map: Map,
        data_extractor: DataExtractorService
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.render2d = render2d
        self.task_manager = task_manager
        self.loader = loader
        self.width = 215
        self._height: float | None = None
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.circuit_map = circuit_map
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render)

        self.frame: DirectFrame | None = None
        self.f1_logo: OnscreenImage | None = None
        self.lap_counter: DirectLabel | None = None
        self.mode: str = "interval"
        self.team_colors: list[DirectFrame] = []
        self.driver_abbreviations: list[DirectLabel] = []
        self.driver_times: list[DirectLabel] = []
        self.driver_tires: list[DirectLabel] = []

        self.sorted_drivers: list[Driver] = self.circuit_map.drivers

        self._total_laps: int | None = None

    @property
    def height(self) -> float:
        if self._height is None:
            self._height = 25 + 50 + (len(self.circuit_map.drivers) * 23)

        return self._height

    @property
    def total_laps(self) -> int:
        if self._total_laps is None:
            self._total_laps = self.data_extractor.session.total_laps

        return self._total_laps

    @property
    def laps(self) -> Laps:
        return self.data_extractor.laps

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.18, 0.18, 0.18, 0.8),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(10, 0, -50)
        )

    def render_f1_logo(self) -> None:
        self.f1_logo = OnscreenImage(
            image='./src/f1p/ui/images/f1_logo.png',
            pos=Point3(self.width / 2, 0, -25),
            scale=self.width / 4,
            parent=self.frame,
        )
        self.f1_logo.setTransparency(TransparencyAttrib.MAlpha)

    def render_lap_counter(self) -> None:
        self.lap_counter = DirectLabel(
            parent=self.frame,
            pos=Point3(self.width / 2, 0, -65),
            scale=self.width / 10,
            frameColor=(0.1, 0.1, 0.1, 0.0),
            text_fg=(1, 1, 1, 0.8),
            text_font=self.text_font,
            text=f'LAP 1/{self.total_laps}',  # TODO grab actual laps and lap count
        )

    def switch_mode(self, mode: str) -> None:
        match mode:
            case "🕒":
                self.mode = "interval"
            case "🕘":
                self.mode = "leader"
            case "🛠":
                self.mode = "pits"
            case "⛁":
                self.mode = "tires"

    def render_mode_selector(self) -> None:
        BlackDropDown(
            parent=self.frame,
            width=40,
            height=30,
            font=self.symbols_font,
            font_scale=20,
            popup_menu_below=True,
            command=self.switch_mode,
            text="leaderboard",
            text_pos=(20, -5),
            text_align=TextNode.ACenter,
            item_text_align=TextNode.ACenter,
            items=["🕒", "🕘", "🛠", "⛁"],
            item_scale=1.0,
            initialitem=0,
            pos=Point3(self.width - 45, 0, -19),
        ),

    def render_drivers(self) -> None:
        for index, driver in enumerate(self.sorted_drivers):
            DirectLabel(
                parent=self.frame,
                pos=Point3(20, 0, -85 - (index * 23)),
                scale=self.width / 14,
                frameColor=(0, 0, 0, 0),
                text_fg=(1, 1, 1, 0.8),
                text_font=self.text_font,
                text=str(index + 1),
            )

            self.team_colors.append(
                DirectFrame(
                    parent=self.frame,
                    frameColor=driver.team_color_obj,
                    frameSize=(0, 12, 0, 12),
                    pos=Point3(40, 0, -87 - (index * 23))
                )
            )

            self.driver_abbreviations.append(
                DirectLabel(
                    parent=self.frame,
                    pos=Point3(80, 0, -85 - (index * 23)),
                    scale=self.width / 14,
                    frameColor=(0, 0, 0, 0),
                    text_fg=(1, 1, 1, 0.8),
                    text_font=self.text_font,
                    text=driver.abbreviation,
                )
            )

            self.driver_times.append(
                DirectLabel(
                    parent=self.frame,
                    pos=Point3(145, 0, -85 - (index * 23)),
                    scale=self.width / 14,
                    frameColor=(0, 0, 0, 0),
                    text_fg=(1, 1, 1, 0.8),
                    text_font=self.text_font,
                    text="Interval",
                )
            )

            self.driver_tires.append(
                DirectLabel(
                    parent=self.frame,
                    pos=Point3(200, 0, -85 - (index * 23)),
                    scale=self.width / 14,
                    frameColor=(0, 0, 0, 0),
                    text_fg=(1, 0, 0, 0.8),
                    text_font=self.text_font,
                    text="S",
                )
            )

    def update(self, session_time: Timedelta) -> None:
        laps_passed = self.laps[self.laps["LapStartTime"] <= session_time]
        current_lap = int(laps_passed["LapNumber"].max())

        self.lap_counter["text"] = f"LAP {current_lap}/{self.total_laps}"

        for driver in self.sorted_drivers:
            driver_laps = laps_passed[laps_passed["Driver"] == driver.abbreviation]
            driver.current_lap = driver_laps[driver_laps["LapNumber"] == driver_laps["LapNumber"].max()]

        self.sorted_drivers = sorted(self.sorted_drivers, key=lambda d: d.current_position)

        driver_in_front = None
        time_to_leader = Timedelta(milliseconds=0)

        for index, driver in enumerate(self.sorted_drivers):
            self.team_colors[index]["frameColor"] = driver.team_color_obj
            self.driver_abbreviations[index]["text"] = driver.abbreviation

            driver.set_time_to_car_in_front(driver_in_front, session_time)
            driver.set_time_to_leader(time_to_leader)

            if driver.is_in_pit(session_time):
                self.driver_times[index]["text_fg"] = driver.team_color_obj
                self.driver_times[index]["text"] = "IN PIT"
            else:
                self.driver_times[index]["text_fg"] = (1, 1, 1, 0.8)
                match self.mode:
                    case "interval":
                        if index > 0:
                            self.driver_times[index]["text"] = driver.formatted_time_to_car_in_front
                        else:
                            self.driver_times[index]["text"] = "Interval"
                    case "leader":
                        if index > 0:
                            self.driver_times[index]["text"] = driver.formatted_time_to_leader
                        else:
                            self.driver_times[index]["text"] = "Leader"

            self.driver_tires[index]["text_fg"] = driver.current_tire_compound_color
            self.driver_tires[index]["text"] = driver.current_tire_compound

            driver_in_front = driver
            time_to_leader += driver.time_to_car_in_front


    def render(self) -> None:
        self.render_frame()
        self.render_f1_logo()
        self.render_lap_counter()
        self.render_mode_selector()
        self.render_drivers()
