from decimal import Decimal
from math import ceil

import pandas as pd
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.ShowBase import ShowBase
from panda3d.core import (
    Camera,
    GraphicsWindow,
    LineSegs,
    LVecBase4f,
    NodePath,
    PerspectiveLens,
    PGTop,
    Point3,
    TextNode,
    VBase4,
    Vec4,
    WindowProperties,
)
from pandas import DataFrame, Series

from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.enums import Colors
from f1p.utils.timedelta import td_to_min_n_sec


class DriverWindow(DirectObject):
    def __init__(
        self,
        width: int,
        height: int,
        driver_number: str,
        first_name: str,
        last_name: str,
        team_color_obj: LVecBase4f,
        team_name: str,
        app: ShowBase,
        data_extractor: DataExtractorService,
    ):
        super().__init__()

        self.width = width
        self.height = height
        self.driver_frame_height = 380
        self.telemetry_frame_height = 225
        self.laps_widget_width = 510

        self.driver_number = driver_number
        self.first_name = first_name
        self.last_name = last_name
        self.team_color_obj = team_color_obj
        self.team_name = team_name
        self.app = app
        self.data_extractor = data_extractor

        self.total_laps = self.data_extractor.total_laps
        self.is_open = False

        self._strategy: dict[int, dict[str, str | int]] | None = None
        self._driver_laps: DataFrame | None = None
        self._slowest_non_pit_lap: Series | None = None
        self._slowest_driver_lap: Series | None = None
        self._fastest_driver_lap: Series | None = None
        self._normalized_driver_laps: DataFrame | None = None
        self._window_properties: WindowProperties | None = None
        self._window: GraphicsWindow | None = None

        self._render2d: NodePath | None = None
        self._pixel2d: NodePath | None = None

        self._lens: PerspectiveLens | None = None
        self._camera: Camera | None = None
        self._camera_np: NodePath | None = None

        self.position: OnscreenText | None = None
        self.laps: OnscreenText | None = None
        self.speed_kph: OnscreenText | None = None
        self.speed_mph: OnscreenText | None = None
        self.rpm: DirectFrame | None = None
        self.gear_N: OnscreenText | None = None
        self.gear_1: OnscreenText | None = None
        self.gear_2: OnscreenText | None = None
        self.gear_3: OnscreenText | None = None
        self.gear_4: OnscreenText | None = None
        self.gear_5: OnscreenText | None = None
        self.gear_6: OnscreenText | None = None
        self.gear_7: OnscreenText | None = None
        self.gear_8: OnscreenText | None = None
        self.drs: OnscreenText | None = None
        self.brake: DirectFrame | None = None
        self.throttle: DirectFrame | None = None
        self.lap_time_line: DirectFrame | None = None

        self.current_lap_identifier: OnscreenText | None = None
        self.current_lap_number: OnscreenText | None = None
        self.current_lap_tires: OnscreenText | None = None
        self.current_lap_s1: OnscreenText | None = None
        self.current_lap_s2: OnscreenText | None = None
        self.current_lap_s3: OnscreenText | None = None
        self.current_lap_time: OnscreenText | None = None

        self.blue_color = (103 / 255, 190 / 255, 217 / 255, 1)
        self.green_color = (102 / 255, 217 / 255, 126 / 255, 1)
        self.red_color = (217 / 255, 110 / 255, 102 / 255, 1)
        self.white_color = (1, 1, 1, 1)
        self.gray_color = (0.7, 0.7, 0.7, 1)
        self.dark_gray_color = (0.5, 0.5, 0.5, 1)
        self.purple_color = (1, 0, 1, 0.6)
        self.highlighter_yellow_color = (0.8, 1, 0, 1)

        self.accept(f"closeDriver{self.driver_number}", self.close)

    @property
    def strategy(self) -> dict[int, dict[str, str | int]]:
        if self._strategy is None:
            self._strategy = self.data_extractor.extract_tire_strategy(
                self.driver_number
            )

        return self._strategy

    @property
    def driver_laps(self) -> DataFrame:
        if self._driver_laps is None:
            df = self.data_extractor.laps.copy()
            df = df[df["DriverNumber"] == self.driver_number].copy()

            df["S2LapTime"] = df["Sector2SessionTime"] - df["LapStartTime"]

            self._driver_laps = df

        return self._driver_laps

    @property
    def slowest_non_pit_lap(self) -> Series:
        if self._slowest_non_pit_lap is None:
            df = self.data_extractor.laps.copy()

            self._slowest_non_pit_lap = (
                df[
                    df["PitInTimeMilliseconds"].isna()
                    & df["PitOutTimeMilliseconds"].isna()
                    & (df["TrackStatus"] == "1")
                ]
                .sort_values("LapTime", ascending=False)
                .iloc[0]
            )

        return self._slowest_non_pit_lap

    @property
    def slowest_driver_lap(self) -> Series:
        if self._slowest_driver_lap is None:
            df = self.driver_laps.copy()

            self._slowest_driver_lap = (
                df[
                    df["PitInTimeMilliseconds"].isna()
                    & df["PitOutTimeMilliseconds"].isna()
                    & (df["TrackStatus"] == "1")
                ]
                .sort_values("LapTime", ascending=False)
                .iloc[0]
            )

        return self._slowest_driver_lap

    @property
    def fastest_driver_lap(self) -> Series:
        if self._fastest_driver_lap is None:
            df = self.driver_laps.copy()

            self._fastest_driver_lap = (
                df[
                    df["PitInTimeMilliseconds"].isna()
                    & df["PitOutTimeMilliseconds"].isna()
                    & (df["TrackStatus"] == "1")
                ]
                .sort_values("LapTime", ascending=True)
                .iloc[0]
            )

        return self._fastest_driver_lap

    @property
    def normalized_driver_laps(self) -> DataFrame:
        if self._normalized_driver_laps is None:
            df = self.driver_laps.copy()
            slowest_time = self.slowest_non_pit_lap["LapTime"].total_seconds()

            df["NormalizedLapTime"] = df["LapTime"].dt.total_seconds() / slowest_time
            df.loc[df["NormalizedLapTime"] > 1, "NormalizedLapTime"] = 1.0
            df["NormalizedS1Time"] = df["Sector1Time"].dt.total_seconds() / slowest_time
            df.loc[df["NormalizedS1Time"] > 1, "NormalizedS1Time"] = 1.0
            df["NormalizedS2Time"] = df["S2LapTime"].dt.total_seconds() / slowest_time
            df.loc[df["NormalizedS2Time"] > 1, "NormalizedS2Time"] = 1.0

            self._normalized_driver_laps = df

        return self._normalized_driver_laps

    @property
    def window_properties(self) -> WindowProperties:
        if self._window_properties is None:
            self._window_properties = WindowProperties()
            self._window_properties.setSize(self.width, self.height)
            self._window_properties.setFixedSize(True)
            self._window_properties.setTitle(
                f"Driver {self.driver_number} - {self.first_name} {self.last_name}"
            )

        return self._window_properties

    @property
    def window(self) -> GraphicsWindow:
        if self._window is None:
            self._window = self.app.openWindow(
                props=self.window_properties, makeCamera=False
            )
            self._window.setCloseRequestEvent(f"closeDriver{self.driver_number}")
            self._window.setClearColor(VBase4(0.3, 0.3, 0.3, 1))

        return self._window

    @property
    def render2d(self) -> NodePath:
        if self._render2d is None:
            self._render2d = NodePath(f"render2d{self.driver_number}")
            self._render2d.setDepthTest(False)
            self._render2d.setDepthWrite(False)

            camera2d_np = self.app.makeCamera2d(self.window)
            camera2d_np.reparentTo(self._render2d)

        return self._render2d

    @property
    def pixel2d(self) -> NodePath:
        if self._pixel2d is None:
            self._pixel2d = self.render2d.attachNewNode(
                PGTop(f"pixel2d{self.driver_number}")
            )
            self._pixel2d.setPos(-1, 0, 1)
            width, height = self.window.getSize()
            self._pixel2d.setScale(2.0 / width, 1.0, 2.0 / height)
            self._pixel2d.reparentTo(self.render2d)

        return self._pixel2d

    @property
    def lens(self) -> PerspectiveLens:
        if self._lens is None:
            self._lens = PerspectiveLens()
            self._lens.setAspectRatio(640 / 480)

        return self._lens

    @property
    def camera(self) -> Camera:
        if self._camera is None:
            self._camera = Camera(f"camera{self.driver_number}")
            self._camera.setLens(self.lens)

        return self._camera

    @property
    def camera_np(self) -> NodePath:
        if self._camera_np is None:
            self._camera_np = NodePath(self.camera)
            self._camera_np.reparentTo(self.app.render)

        return self._camera_np

    def make_camera_region(self) -> None:
        dr = self.window.makeDisplayRegion(
            (self.width - 260) / self.width,
            (self.width - 20) / self.width,
            355 / self.height,
            595 / self.height,
        )
        dr.setSort(10)
        dr.setClearColorActive(True)
        dr.setClearColor(Vec4(0.3, 0.3, 0.3, 1))
        dr.setCamera(self.camera_np)

    def make_driver_widget(self) -> None:
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, 260, 0, self.driver_frame_height),
            pos=Point3(
                530, 0, -(self.height - (self.height - self.driver_frame_height - 10))
            ),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, 260, 0, title_frame_height),
            pos=Point3(0, 0, self.driver_frame_height - title_frame_height),
            sortOrder=10,
        )

        OnscreenText(
            parent=title_frame,
            text="DRIVER",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(260 / 2, title_frame_height - 20, 0),
        )

        OnscreenText(
            parent=frame,
            text=f"#{self.driver_number} {self.first_name} {self.last_name}",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(10, self.driver_frame_height - title_frame_height - 25, 0),
        )

        DirectFrame(
            parent=frame,
            frameColor=self.team_color_obj,
            frameSize=(0, 19, 0, 19),
            pos=(10, 0, self.driver_frame_height - title_frame_height - 54),
            sortOrder=20,
        )

        OnscreenText(
            parent=frame,
            text=self.team_name,
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 1),
            pos=(33, self.driver_frame_height - title_frame_height - 50, 0),
        )

        OnscreenText(
            parent=frame,
            text="POSITION",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(10, self.driver_frame_height - title_frame_height - 70, 0),
        )

        self.position = OnscreenText(
            parent=frame,
            text="TBD",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(10, self.driver_frame_height - title_frame_height - 90, 0),
        )

        OnscreenText(
            parent=frame,
            text="LAPS",
            align=TextNode.ALeft,
            scale=13,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(100, self.driver_frame_height - title_frame_height - 70, 0),
        )

        self.laps = OnscreenText(
            parent=frame,
            text=f"TBD/{self.total_laps}",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=(1, 1, 1, 0.8),
            pos=(120, self.driver_frame_height - title_frame_height - 90, 0),
        )

    def make_telemetry_widget(self) -> None:
        width = 260
        frame_z = -(
            self.height
            - (
                self.height
                - self.telemetry_frame_height
                - self.driver_frame_height
                - 20
            )
        )
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, width, 0, self.telemetry_frame_height),
            pos=Point3(530, 0, frame_z),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, self.telemetry_frame_height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="TELEMETRY",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, title_frame_height - 21, 0),
        )

        OnscreenText(
            parent=frame,
            text="GEARS",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 20, 0),
        )

        gear_spacer = 20
        initial_space = 45
        self.gear_N = OnscreenText(
            parent=frame,
            text="N",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.green_color,
            pos=(
                initial_space,
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_1 = OnscreenText(
            parent=frame,
            text="1",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 1),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_2 = OnscreenText(
            parent=frame,
            text="2",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 2),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_3 = OnscreenText(
            parent=frame,
            text="3",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 3),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_4 = OnscreenText(
            parent=frame,
            text="4",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 4),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_5 = OnscreenText(
            parent=frame,
            text="5",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 5),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_6 = OnscreenText(
            parent=frame,
            text="6",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 6),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_7 = OnscreenText(
            parent=frame,
            text="7",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 7),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        self.gear_8 = OnscreenText(
            parent=frame,
            text="8",
            align=TextNode.ALeft,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(
                initial_space + (gear_spacer * 8),
                self.telemetry_frame_height - title_frame_height - 40,
                0,
            ),
        )

        rpm_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(0, 240, 0, 10),
            pos=Point3(10, 0, self.telemetry_frame_height - title_frame_height - 60),
        )

        self.rpm = DirectFrame(
            parent=rpm_frame,
            frameColor=self.blue_color,
            frameSize=(0, 0, 0, 10),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ALeft,
            scale=11,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(10, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        OnscreenText(
            parent=frame,
            text="15",
            align=TextNode.ARight,
            scale=11,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(width - 10, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        OnscreenText(
            parent=frame,
            text="RPM x1000",
            align=TextNode.ACenter,
            scale=11,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 70, 0),
        )

        brake_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(60, 0, self.telemetry_frame_height - title_frame_height - 170),
        )
        self.brake = DirectFrame(
            parent=brake_frame,
            frameColor=self.red_color,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="BRAKE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(60, self.telemetry_frame_height - title_frame_height - 185, 0),
        )

        OnscreenText(
            parent=frame,
            text="KM/H",
            align=TextNode.ACenter,
            scale=15,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 90, 0),
        )

        self.speed_kph = OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ACenter,
            scale=18,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 110, 0),
        )

        self.drs = OnscreenText(
            parent=frame,
            text="DRS",
            align=TextNode.ACenter,
            scale=14,
            font=self.app.text_font,
            fg=self.blue_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 132, 0),
        )

        self.speed_mph = OnscreenText(
            parent=frame,
            text="0",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.dark_gray_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 155, 0),
        )

        OnscreenText(
            parent=frame,
            text="MPH",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.dark_gray_color,
            pos=(width / 2, self.telemetry_frame_height - title_frame_height - 170, 0),
        )

        throttle_frame = DirectFrame(
            parent=frame,
            frameColor=self.gray_color,
            frameSize=(-10, 10, 0, 100),
            pos=Point3(
                width - 60, 0, self.telemetry_frame_height - title_frame_height - 170
            ),
        )
        self.throttle = DirectFrame(
            parent=throttle_frame,
            frameColor=self.green_color,
            frameSize=(-10, 10, 0, 0),
            pos=Point3(0, 0, 0),
        )

        OnscreenText(
            parent=frame,
            text="THROTTLE",
            align=TextNode.ACenter,
            scale=13,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(width - 60, self.telemetry_frame_height - title_frame_height - 185, 0),
        )

    def make_tire_strategy_widget(self) -> None:
        height = 90
        width = 260
        frame_z = -(
            self.height
            - (
                self.height
                - height
                - self.driver_frame_height
                - self.telemetry_frame_height
                - 30
            )
        )
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, width, 0, height),
            pos=Point3(530, 0, frame_z),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, width, 0, title_frame_height),
            pos=Point3(0, 0, height - title_frame_height),
            sortOrder=10,
        )
        title_frame.clearColorScale()

        OnscreenText(
            parent=title_frame,
            text="TIRE STRATEGY",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(width / 2, title_frame_height - 21, 0),
        )

        padding = 10
        total_width = width - (padding * 2)
        total_laps = max(i["TotalLaps"] for i in self.strategy.values())
        start = padding + 0

        for _, info in self.strategy.items():
            current_ratio = info["LapNumber"] / total_laps
            end = padding + (total_width * current_ratio)

            DirectFrame(
                parent=frame,
                frameColor=(0.4, 0.4, 0.4, 1),
                frameSize=(start, end, 0, 30),
                pos=Point3(0, 0, height - title_frame_height - 40),
            )
            DirectFrame(
                parent=frame,
                frameColor=info["CompoundColor"],
                frameSize=(start + 1, end - 1, 1, 29),
                pos=Point3(1, 0, height - title_frame_height - 41),
            )

            OnscreenText(
                parent=frame,
                text=f"{info['LapNumber']:.0f}",
                align=TextNode.ACenter,
                scale=11,
                font=self.app.text_font,
                fg=self.highlighter_yellow_color,
                pos=(end, height - title_frame_height - 50, 0),
            )
            start = end

        OnscreenText(
            parent=frame,
            text="1",
            align=TextNode.ACenter,
            scale=11,
            font=self.app.text_font,
            fg=self.highlighter_yellow_color,
            pos=(10, height - title_frame_height - 50, 0),
        )

    def draw_lap(
        self,
        height: float,
        title_frame_height: float,
        frame: DirectFrame,
        lap_number: int,
    ) -> None:
        offset = lap_number * 15
        text_scale = 9

        OnscreenText(
            parent=frame,
            text=f"{lap_number}",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(10, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="M(4)",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(30, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="29.223",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(70, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="31.234",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(110, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="36.123",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(140, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="1:36.580",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(170, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="123km/h",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(200, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="314km/h",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(230, height - title_frame_height - 21 - offset, 0),
        )

        OnscreenText(
            parent=frame,
            text="340km/h",
            align=TextNode.ALeft,
            scale=text_scale,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(260, height - title_frame_height - 21 - offset, 0),
        )

    def draw_chart_line(
        self,
        frame: DirectFrame,
        chart_height: float,
        top_gap: float,
        height: float,
        title_frame_height: float,
        times: DataFrame,
        color: tuple[float, float, float, float],
        shift_x: float = 0,
    ) -> None:
        offset_x = (self.laps_widget_width - 90) / self.total_laps
        offset_y = chart_height

        points = []
        for lap in times.itertuples():
            i = int(lap.LapNumber)
            x = 80 + (offset_x * i) - (shift_x * offset_x)
            y = (
                height
                - title_frame_height
                - chart_height
                - top_gap
                + (offset_y * lap.Time)
            )

            points.append(Point3(x, 0, y))

        line_segments = LineSegs()
        line_segments.setThickness(1)
        line_segments.setColor(color)

        for i in range(len(points) - 1):
            line_segments.moveTo(points[i])
            line_segments.drawTo(points[i + 1])

        node_path = NodePath(line_segments.create(False))
        node_path.reparentTo(frame)

    def draw_lap_time_chart(
        self,
        frame: DirectFrame,
        height: float,
        title_frame_height: float,
        chart_height: float,
    ) -> None:
        top_gap = 10

        # Y-axis
        DirectFrame(
            parent=frame,
            frameColor=self.white_color,
            frameSize=(0, 2, 0, chart_height),
            pos=Point3(80, 0, height - title_frame_height - chart_height - top_gap),
        )

        slowest_lap_time = self.slowest_non_pit_lap["LapTime"].total_seconds()

        # Y-axis lines
        for i in range(5, ceil(slowest_lap_time) + 1, 5):
            offset = chart_height / slowest_lap_time

            DirectFrame(
                parent=frame,
                frameColor=self.dark_gray_color,
                frameSize=(0, self.laps_widget_width - 85, 0, 1),
                pos=Point3(
                    75,
                    0,
                    height - title_frame_height - chart_height - top_gap + (offset * i),
                ),
            )

            minutes = i // 60
            seconds = i % 60

            OnscreenText(
                parent=frame,
                text=f"{minutes}:{seconds:02d}.000",
                align=TextNode.ALeft,
                scale=11,
                font=self.app.text_font,
                fg=self.white_color,
                pos=(
                    10,
                    height
                    - title_frame_height
                    - chart_height
                    - top_gap
                    + (offset * i)
                    - 3,
                    0,
                ),
            )

        # X-axis
        DirectFrame(
            parent=frame,
            frameColor=self.white_color,
            frameSize=(0, self.laps_widget_width - 90, 0, 2),
            pos=Point3(80, 0, height - title_frame_height - chart_height - top_gap),
        )

        # X-axis lines
        for i in range(5, self.total_laps + 1, 5):
            offset = (self.laps_widget_width - 90) / self.total_laps

            DirectFrame(
                parent=frame,
                frameColor=self.dark_gray_color,
                frameSize=(0, 1, -5, chart_height),
                pos=Point3(
                    80 + (offset * i),
                    0,
                    height - title_frame_height - chart_height - top_gap,
                ),
            )

            OnscreenText(
                parent=frame,
                text=f"{i}",
                align=TextNode.ACenter,
                scale=12,
                font=self.app.text_font,
                fg=self.highlighter_yellow_color,
                pos=(
                    80 + (offset * i),
                    height - title_frame_height - chart_height - top_gap - 20,
                    0,
                ),
            )

        # Draw Lap Times Line
        lap_times = (
            self.normalized_driver_laps[["LapNumber", "NormalizedLapTime"]]
            .sort_values("LapNumber")
            .rename(columns={"NormalizedLapTime": "Time"})
        )
        self.draw_chart_line(
            frame,
            chart_height,
            top_gap,
            height,
            title_frame_height,
            lap_times,
            self.blue_color,
        )
        # Draw S1 Times Line
        s1_times = (
            self.normalized_driver_laps[["LapNumber", "NormalizedS1Time"]]
            .sort_values("LapNumber")
            .rename(columns={"NormalizedS1Time": "Time"})
        )
        self.draw_chart_line(
            frame,
            chart_height,
            top_gap,
            height,
            title_frame_height,
            s1_times,
            self.gray_color,
            shift_x=2 / 3,
        )
        # Draw S2 Times Line
        s2_times = (
            self.normalized_driver_laps[["LapNumber", "NormalizedS2Time"]]
            .sort_values("LapNumber")
            .rename(columns={"NormalizedS2Time": "Time"})
        )
        self.draw_chart_line(
            frame,
            chart_height,
            top_gap,
            height,
            title_frame_height,
            s2_times,
            self.red_color,
            shift_x=1 / 3,
        )

        self.lap_time_line = DirectFrame(
            parent=frame,
            frameColor=self.highlighter_yellow_color,
            frameSize=(0, 1, -5, chart_height),
            pos=Point3(
                80,
                0,
                height - title_frame_height - chart_height - top_gap,
            ),
        )

    def draw_lap_stats_header(
        self,
        frame: DirectFrame,
        height: float,
        title_frame_height: float,
        chart_height: float,
    ) -> None:
        top_gap = 60
        y = height - title_frame_height - chart_height - top_gap
        x = 80

        columns = {
            "#": 0,
            "Tires": 40,
            "S1": 95,
            "S2": 165,
            "S3": 235,
            "Time": 335,
        }

        for label, offset in columns.items():
            OnscreenText(
                parent=frame,
                text=label,
                align=TextNode.ACenter,
                scale=11,
                font=self.app.text_font,
                fg=self.white_color,
                pos=(x + offset, y, 0),
            )

    def draw_lap_stats(
        self,
        frame: DirectFrame,
        height: float,
        title_frame_height: float,
        chart_height: float,
        heading: str,
        top_gap: int,
        lap: Series,
        updateable: bool = False,
    ) -> None:
        y = height - title_frame_height - chart_height - top_gap
        x = 80

        columns = [
            {
                "field": "identifier",
                "label": heading,
                "offset": -45,
                "color": Colors.WHITE,
            },
            {
                "field": "number",
                "label": str(int(lap["LapNumber"])),
                "offset": 0,
                "color": Colors.WHITE,
            },
            {
                "field": "tires",
                "label": f"{lap['Compound']}({int(lap['TyreLife'])})",
                "offset": 40,
                "color": lap["CompoundColor"],
            },
            {
                "field": "s1",
                "label": td_to_min_n_sec(lap["Sector1Time"]),
                "offset": 95,
                "color": lap["Sector1Color"],
            },
            {
                "field": "s2",
                "label": td_to_min_n_sec(lap["Sector2Time"]),
                "offset": 165,
                "color": lap["Sector2Color"],
            },
            {
                "field": "s3",
                "label": td_to_min_n_sec(lap["Sector3Time"]),
                "offset": 235,
                "color": lap["Sector3Color"],
            },
            {
                "field": "time",
                "label": f"{td_to_min_n_sec(lap['LapTime'])}({lap['LapTimeRatio']:.3f}%)",
                "offset": 335,
                "color": lap["LapTimeColor"],
            },
        ]

        for column in columns:
            text = OnscreenText(
                parent=frame,
                text=column["label"],
                align=TextNode.ACenter,
                scale=11,
                font=self.app.text_font,
                fg=column["color"],
                pos=(x + column["offset"], y, 0),
            )

            if updateable:
                setattr(self, f"current_lap_{column['field']}", text)

    def make_laps_widget(self) -> None:
        height = self.height - 20
        frame_z = -(self.height - (self.height - height - 10))
        frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.2, 0.2, 0.2, 0.7),
            frameSize=(0, self.laps_widget_width, 0, height),
            pos=Point3(10, 0, frame_z),
            sortOrder=0,
        )

        title_frame_height = 30
        title_frame = DirectFrame(
            parent=frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, self.laps_widget_width, 0, title_frame_height),
            pos=Point3(0, 0, height - title_frame_height),
            sortOrder=10,
        )

        OnscreenText(
            parent=title_frame,
            text="LAPS",
            align=TextNode.ACenter,
            scale=16,
            font=self.app.text_font,
            fg=self.white_color,
            pos=(self.laps_widget_width / 2, title_frame_height - 21, 0),
        )

        chart_height = height - title_frame_height - 135

        pd.set_option("display.max_colwidth", None)
        pd.set_option("display.width", 370)
        pd.set_option("display.max_columns", None)

        self.draw_lap_time_chart(frame, height, title_frame_height, chart_height)
        self.draw_lap_stats_header(frame, height, title_frame_height, chart_height)
        self.draw_lap_stats(
            frame,
            height,
            title_frame_height,
            chart_height,
            "Slowest",
            80,
            self.slowest_driver_lap,
        )
        self.draw_lap_stats(
            frame,
            height,
            title_frame_height,
            chart_height,
            "Fastest",
            100,
            self.fastest_driver_lap,
        )
        self.draw_lap_stats(
            frame,
            height,
            title_frame_height,
            chart_height,
            "Current",
            120,
            self.driver_laps[self.driver_laps["LapNumber"] == 1].iloc[0],
            updateable=True,
        )

    def update_standings(
        self, position_index: int, lap: float, total_laps: float
    ) -> None:
        if self.position.text != f"{position_index + 1}":
            self.position["text"] = f"{position_index + 1}"

        if self.laps.text != f"{int(lap)}/{total_laps:.0f}":
            self.laps["text"] = f"{int(lap)}/{total_laps:.0f}"

    def update_gear_indicator(self, indicator: str, gear: str) -> None:
        indicator_property = getattr(self, f"gear_{indicator}")

        current_gear_color = indicator_property.textNode.getTextColor()
        gear_color = self.green_color if gear == indicator else self.gray_color
        if current_gear_color != gear_color:
            indicator_property["fg"] = gear_color

    def update_drs_indicator(self, drs: int) -> None:
        current_drs_color = self.drs.textNode.getTextColor()

        drs_color = self.blue_color
        match drs:
            case 0:
                drs_color = self.blue_color
            case 1:
                drs_color = self.red_color
            case 14:
                drs_color = self.green_color

        if current_drs_color != drs_color:
            self.drs["fg"] = drs_color

    def update_telemetry(
        self,
        gear: str,
        rpm: float,
        brake: bool,
        speed_kph: float,
        drs: int,
        speed_mph: float,
        throttle: float,
    ) -> None:
        for indicator in ["N", "1", "2", "3", "4", "5", "6", "7", "8"]:
            self.update_gear_indicator(indicator, gear)

        current_rpm_size = self.rpm["frameSize"]
        rpm_size = (0, rpm / 15000 * 240, 0, 10)
        if current_rpm_size != rpm_size:
            self.rpm["frameSize"] = rpm_size

        current_brake_size = self.brake["frameSize"]
        brake_size = (-10, 10, 0, 100 if brake else 0)
        if current_brake_size != brake_size:
            self.brake["frameSize"] = brake_size

        if self.speed_kph.text != f"{speed_kph:.0f}":
            self.speed_kph["text"] = f"{speed_kph:.0f}"

        self.update_drs_indicator(drs)

        if self.speed_mph.text != f"{speed_mph:.0f}":
            self.speed_mph["text"] = f"{speed_mph:.0f}"

        current_throttle_size = self.throttle["frameSize"]
        throttle_size = (-10, 10, 0, throttle)
        if current_throttle_size != throttle_size:
            self.throttle["frameSize"] = throttle_size

    def update_camera_position(self, x: Decimal, y: Decimal, z: Decimal) -> None:
        self.camera_np.setX(x + 5)
        self.camera_np.setY(y + 5)
        self.camera_np.setZ(z + 5)
        self.camera_np.lookAt(x, y, z)

    def update_lap_time_line(self, laps_completed: float) -> None:
        offset = (self.laps_widget_width - 90) / self.total_laps
        self.lap_time_line.setX(80 + (offset * laps_completed))

    def update_current_lap(self, current_record: dict):
        lap_number = str(int(current_record["LapNumber"]))
        if self.current_lap_number["text"] != lap_number:
            self.current_lap_number["text"] = lap_number

        tires = f"{current_record['Compound']}({int(current_record['TyreLife'])})"
        if self.current_lap_tires["text"] != tires:
            self.current_lap_tires["text"] = tires
        current_tires_color = self.current_lap_tires.textNode.getTextColor()
        if current_tires_color != current_record["CompoundColor"]:
            self.current_lap_tires["fg"] = current_record["CompoundColor"]

        s1_time = td_to_min_n_sec(current_record["Sector1Time"])
        if self.current_lap_s1["text"] != s1_time:
            self.current_lap_s1["text"] = s1_time
        current_s1_color = self.current_lap_s1.textNode.getTextColor()
        if current_s1_color != current_record["Sector1Color"]:
            self.current_lap_s1["fg"] = current_record["Sector1Color"]

        s2_time = td_to_min_n_sec(current_record["Sector2Time"])
        if self.current_lap_s2["text"] != s2_time:
            self.current_lap_s2["text"] = s2_time
        current_s2_color = self.current_lap_s2.textNode.getTextColor()
        if current_s2_color != current_record["Sector2Color"]:
            self.current_lap_s2["fg"] = current_record["Sector2Color"]

        s3_time = td_to_min_n_sec(current_record["Sector3Time"])
        if self.current_lap_s3["text"] != s3_time:
            self.current_lap_s3["text"] = s3_time
        current_s3_color = self.current_lap_s3.textNode.getTextColor()
        if current_s3_color != current_record["Sector3Color"]:
            self.current_lap_s3["fg"] = current_record["Sector3Color"]

        lap_time = f"{td_to_min_n_sec(current_record['LapTime'])}({current_record['LapTimeRatio']:.3f}%)"
        if self.current_lap_time["text"] != lap_time:
            self.current_lap_time["text"] = lap_time
        current_time_color = self.current_lap_time.textNode.getTextColor()
        if current_time_color != current_record["LapTimeColor"]:
            self.current_lap_time["fg"] = current_record["LapTimeColor"]

    def update(self, current_record: dict) -> None:
        self.update_standings(
            current_record["PositionIndex"],
            current_record["LapNumber"],
            current_record["TotalLaps"],
        )

        self.update_telemetry(
            current_record["nGear"],
            current_record["RPM"],
            current_record["Brake"],
            current_record["Speed"],
            current_record["DRS"],
            current_record["SpeedMph"],
            current_record["Throttle"],
        )

        precision = Decimal("0.001")
        x = Decimal(current_record["X"]).quantize(precision)
        y = Decimal(current_record["Y"]).quantize(precision)
        z = Decimal(current_record["Z"]).quantize(precision)
        self.update_camera_position(x, y, z)

        self.update_lap_time_line(current_record["LapsCompletion"])
        self.update_current_lap(current_record)

    def open(self) -> None:
        if self.is_open:
            return

        self.is_open = True
        self.make_driver_widget()
        self.make_camera_region()
        self.make_telemetry_widget()
        self.make_tire_strategy_widget()
        self.make_laps_widget()

    def close(self) -> None:
        self.is_open = False
        self.window.removeAllDisplayRegions()
        self.render2d.removeNode()
        self.app.closeWindow(self.window)

        self._window = None
        self._render2d = None
        self._pixel2d = None
        self._lens = None
        self._camera = None
        self._camera_np = None
