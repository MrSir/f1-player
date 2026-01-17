from typing import Any

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task, TaskManager
from fastf1.core import Laps
from panda3d.core import Point3, StaticTextFont, TextNode, TransparencyAttrib

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver
from f1p.ui.components.gui.drop_down import BlackDropDown
from f1p.ui.components.leaderboard.processors import (
    IntervalLeaderboardProcessor,
    LeaderboardProcessor,
    LeaderLeaderboardProcessor,
    TiresLeaderboardProcessor,
)
from f1p.ui.components.map import Map


class Leaderboard(DirectObject):
    def __init__(
        self,
        pixel2d,
        task_manager: TaskManager,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        circuit_map: Map,
        data_extractor: DataExtractorService,
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.task_manager = task_manager
        self.width = 215
        self._height: float | None = None
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.circuit_map = circuit_map
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render_task)
        self.accept("updateLeaderboard", self.update)

        self.frame: DirectFrame | None = None
        self.track_status_frame_top: DirectFrame | None = None
        self.track_status_frame_left: DirectFrame | None = None
        self.track_status_frame_bottom: DirectFrame | None = None
        self.track_status_frame: DirectFrame | None = None
        self.track_status: OnscreenText | None = None
        self.f1_logo: OnscreenImage | None = None
        self.lap_counter: OnscreenText | None = None
        self.mode: str = "interval"
        self.checkered_flags: list[OnscreenText] = []
        self.team_colors: list[DirectFrame] = []
        self.driver_abbreviations: list[OnscreenText] = []
        self.driver_times: list[OnscreenText] = []
        self.driver_tires: list[OnscreenText] = []
        self.has_fastest_lap: list[OnscreenText] = []

        self.drivers: list[Driver] = self.circuit_map.drivers

        self._laps: Laps | None = None
        self._total_laps: int | None = None

    @property
    def height(self) -> float:
        if self._height is None:
            self._height = 130 + (len(self.circuit_map.drivers) * 23)

        return self._height

    @property
    def total_laps(self) -> int:
        if self._total_laps is None:
            self._total_laps = self.data_extractor.session.total_laps

        return self._total_laps

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.20, 0.20, 0.20, 0.7),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(20, 0, -50),
        )

    def render_track_status_frame(self) -> None:
        self.track_status_frame_top = DirectFrame(
            parent=self.frame,
            frameColor=self.data_extractor.green_flag_track_status_color,
            frameSize=(0, self.width - 5, 0, -1),
            pos=Point3(2, 0, -2),
        )

        self.track_status_frame_left = DirectFrame(
            parent=self.frame,
            frameColor=self.data_extractor.green_flag_track_status_color,
            frameSize=(0, 1, 0, self.width - 5),
            pos=Point3(2, 0, -self.width + 3),
        )

    def render_f1_logo(self) -> None:
        self.f1_logo = OnscreenImage(
            image="./src/f1p/ui/images/f1_logo.png",
            pos=Point3(self.width / 2, 0, -27),
            scale=self.width / 4,
            parent=self.frame,
        )
        self.f1_logo.setTransparency(TransparencyAttrib.MAlpha)

    def render_lap_counter(self) -> None:
        lap_counter_background = DirectFrame(
            parent=self.frame,
            frameColor=(0.1, 0.1, 0.1, 0.7),
            frameSize=(0, self.width, 0, 40),
            pos=Point3(0, 0, -90),
        )

        self.lap_counter = OnscreenText(
            parent=lap_counter_background,
            pos=(self.width / 2, 14),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text=f"LAP 1/{self.total_laps}",
        )

    def render_track_status(self) -> None:
        self.track_status_frame = DirectFrame(
            parent=self.frame,
            frameColor=self.data_extractor.green_flag_track_status_color,
            frameSize=(0, self.width - 2, 0, 30),
            pos=Point3(2, 0, -120),
        )

        self.track_status = OnscreenText(
            parent=self.track_status_frame,
            pos=(self.width / 2, 9),
            scale=self.width / 11,
            fg=self.data_extractor.green_flag_track_status_text_color,
            font=self.text_font,
            text=self.data_extractor.green_flag_track_status_label,
        )

    def switch_mode(self, mode: str) -> None:
        match mode:
            case "🕒":
                self.mode = "interval"
            case "🕘":
                self.mode = "leader"
            case "⛁":
                self.mode = "tires"

    def render_mode_selector(self) -> None:
        (
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
                items=["🕒", "🕘", "⛁"],
                item_scale=1.0,
                initialitem=0,
                pos=Point3(self.width - 45, 0, -22),
            ),
        )

    def render_drivers(self) -> None:
        offset_from_top = 140

        for index, driver in enumerate(self.drivers):
            self.checkered_flags.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(-10, -offset_from_top - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.symbols_font,
                    text="",
                ),
            )

            OnscreenText(
                parent=self.frame,
                pos=(20, -offset_from_top - (index * 23)),
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
                    pos=Point3(40, 0, -offset_from_top - 2 - (index * 23)),
                ),
            )

            self.driver_abbreviations.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(80, -offset_from_top - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.text_font,
                    text=driver.abbreviation,
                ),
            )

            self.driver_times.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(145, -offset_from_top - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 1, 1, 0.8),
                    font=self.text_font,
                    text="NO TIME",
                ),
            )

            self.driver_tires.append(
                OnscreenText(
                    parent=self.frame,
                    pos=(200, -offset_from_top - (index * 23)),
                    scale=self.width / 14,
                    fg=(1, 0, 0, 0.8),
                    font=self.text_font,
                    text="S",
                ),
            )

            has_fastest_lap = OnscreenText(
                parent=self.frame,
                pos=(self.width + 10, -offset_from_top - (index * 23)),
                scale=self.width / 14,
                bg=(1, 0, 1, 0.6),
                fg=(1, 1, 1, 0.8),
                font=self.symbols_font,
                text="",
            )
            has_fastest_lap.textNode.setCardAsMargin(0.1, 0.2, 0.1, 0.02)

            self.has_fastest_lap.append(has_fastest_lap)

    def update(self, session_time_tick: int) -> None:
        processor: LeaderboardProcessor | None = None

        match self.mode:
            case "interval":
                processor = IntervalLeaderboardProcessor(
                    self.lap_counter,
                    self.track_status_frame_top,
                    self.track_status_frame_left,
                    self.track_status_frame,
                    self.track_status,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.has_fastest_lap,
                    self.data_extractor,
                )
            case "leader":
                processor = LeaderLeaderboardProcessor(
                    self.lap_counter,
                    self.track_status_frame_top,
                    self.track_status_frame_left,
                    self.track_status_frame,
                    self.track_status,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.has_fastest_lap,
                    self.data_extractor,
                )
            case "tires":
                processor = TiresLeaderboardProcessor(
                    self.lap_counter,
                    self.track_status_frame_top,
                    self.track_status_frame_left,
                    self.track_status_frame,
                    self.track_status,
                    self.drivers,
                    self.checkered_flags,
                    self.team_colors,
                    self.driver_abbreviations,
                    self.driver_times,
                    self.driver_tires,
                    self.has_fastest_lap,
                    self.data_extractor,
                )

        if processor is None:
            return

        processor.update(session_time_tick)

    def render_task(self) -> None:
        self.task_manager.add(self.render, "renderLeaderboard")

    def render(self, task: Task) -> Any:
        self.render_frame()
        self.render_f1_logo()
        self.render_lap_counter()
        self.render_track_status_frame()
        self.render_track_status()
        self.render_mode_selector()
        self.render_drivers()

        return task.done
