from datetime import timedelta

import pandas as pd
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from fastf1.core import Laps
from panda3d.core import StaticTextFont, Point3, Loader, TransparencyAttrib, TextNode
from pandas import DataFrame, Timedelta

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver
from f1p.ui.components.gui.drop_down import BlackDropDown
from f1p.ui.components.leaderboard.processors import LeaderboardProcessor, IntervalLeaderboardProcessor, \
    TiresLeaderboardProcessor, PitsLeaderboardProcessor, LeaderLeaderboardProcessor
from f1p.ui.components.map import Map
from f1p.utils.performance import timeit


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
        self.accept("updateLeaderboard", self.update)

        self.frame: DirectFrame | None = None
        self.f1_logo: OnscreenImage | None = None
        self.lap_counter: OnscreenText | None = None
        self.mode: str = "interval"
        self.checkered_flags: list[OnscreenText] = []
        self.team_colors: list[DirectFrame] = []
        self.driver_abbreviations: list[OnscreenText] = []
        self.driver_times: list[OnscreenText] = []
        self.driver_tires: list[OnscreenText] = []

        self.drivers: list[Driver] = self.circuit_map.drivers

        self._laps: Laps | None = None
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

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.18, 0.18, 0.18, 0.8),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(20, 0, -50)
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
        self.lap_counter = OnscreenText(
            parent=self.frame,
            pos=(self.width / 2, -65),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text=f'LAP 1/{self.total_laps}',
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
        for index, driver in enumerate(self.drivers):
            self.checkered_flags.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(-10, -85 - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.symbols_font,
                    text="",
                )
            )

            OnscreenText(
                parent=self.frame,
                pos=(20, -85 - (index * 23)),
                scale=self.width / 14,
                fg=(1, 1, 1, 0.8),
                font=self.text_font,
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
                OnscreenText(
                    parent=self.frame,
                    pos=(80, -85 - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.text_font,
                    text=driver.abbreviation,
                )
            )

            self.driver_times.append(
                 OnscreenText(
                    parent=self.frame,
                    pos=(145, -85 - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.text_font,
                    text="NO TIME",
                )
            )

            self.driver_tires.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(200, -85 - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 0, 0, 0.8),
                    font=self.text_font,
                    text="S",
                )
            )

    def update(self, session_time_tick: int) -> None:
        processor: LeaderboardProcessor | None = None

        match self.mode:
            case "interval":
                processor = IntervalLeaderboardProcessor(
                    self.lap_counter,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.data_extractor,
                )
            case "leader":
                processor = LeaderLeaderboardProcessor(
                    self.lap_counter,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.data_extractor,
                )
            case "pits":
                processor = PitsLeaderboardProcessor(
                    self.lap_counter,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.data_extractor,
                )
            case "tires":
                processor = TiresLeaderboardProcessor(
                    self.lap_counter,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.data_extractor,
                )

        if processor is None:
            return

        processor.update(session_time_tick)

    def render(self) -> None:
        self.render_frame()
        self.render_f1_logo()
        self.render_lap_counter()
        self.render_mode_selector()
        self.render_drivers()
