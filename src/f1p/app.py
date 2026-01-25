from typing import Self

from direct.showbase.ShowBase import ShowBase
from direct.task import Task
from panda3d.core import PStatClient, WindowProperties, Camera

from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.leaderboard.component import Leaderboard
from f1p.ui.components.map import Map
from f1p.ui.components.menu import Menu
from f1p.ui.components.origin import Origin
from f1p.ui.components.playback import PlaybackControls
from f1p.ui.components.weather import WeatherBoard


class F1PlayerApp(ShowBase):
    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        draw_origin: bool = False,
        show_frame_rate: bool = False,
        pstat_debug: bool = False,
    ):
        super().__init__(self)

        self.symbols_font = self.loader.loadFont("./src/f1p/ui/fonts/NotoSansSymbols2-Regular.ttf")
        self.text_font = self.loader.loadFont("./src/f1p/ui/fonts/f1_font.ttf")

        self.width = width
        self.height = height

        self._data_extractor: DataExtractorService | None = None

        self.default_camera: Camera = self.cam
        self.default_camera.setPos(0, -70, 40)
        self.default_camera.lookAt(0, 0, 0)

        self.setBackgroundColor(0.3, 0.3, 0.3, 1)

        self.cam_controls_enabled = False
        self.zoom = 0

        self.taskMgr.setupTaskChain("loadingData", numThreads=1)

        self.accept("sessionSelected", self.enable_camera_controls)
        self.accept("wheel_up", self.zoom_camera_in)
        self.accept("wheel_down", self.zoom_camera_out)

        self.ui_components: list = []

        if draw_origin:
            origin = Origin(self.render)
            origin.render()

        self.setFrameRateMeter(show_frame_rate)

        if pstat_debug:
            PStatClient.connect()

    @property
    def data_extractor(self) -> DataExtractorService:
        if self._data_extractor is None:
            self._data_extractor = DataExtractorService(
                self.pixel2d,
                self.taskMgr,
                self.width,
                self.height,
                self.text_font,
            )

        return self._data_extractor

    def configure_window(self) -> Self:
        props = WindowProperties()
        props.setSize(self.width, self.height)
        props.setFixedSize(True)
        self.win.requestProperties(props)

        return self

    def draw_menu(self) -> Self:
        menu = Menu(self.pixel2d, self.taskMgr, self.messenger, self.width, 40, self.text_font, self.data_extractor)
        menu.render()

        return self

    def register_ui_components(self) -> Self:
        playback_controls = PlaybackControls(
            self.pixel2d,
            self.default_camera,
            self.taskMgr,
            self.height,
            self.width,
            30,
            self.symbols_font,
            self.text_font,
            self.data_extractor,
        )

        circuit_map = Map(self.render, self.taskMgr, self.data_extractor)

        leaderboard = Leaderboard(
            self.pixel2d,
            self.taskMgr,
            self.symbols_font,
            self.text_font,
            circuit_map,
            self.data_extractor,
        )

        weather_board = WeatherBoard(
            self.pixel2d,
            self.taskMgr,
            self.symbols_font,
            self.text_font,
            self.width,
            self.data_extractor,
        )

        self.ui_components = [
            playback_controls,
            circuit_map,
            leaderboard,
            weather_board,
        ]

        return self

    def enable_camera_controls(self) -> None:
        self.cam_controls_enabled = True

    def zoom_camera_in(self) -> None:
        if not self.cam_controls_enabled:
            return

        if self.zoom + 1 > 100:
            self.zoom = 100
            return

        self.zoom += 1

        self.zoom_camera()

    def zoom_camera_out(self) -> None:
        if not self.cam_controls_enabled:
            return

        if self.zoom - 1 < 0:
            self.zoom = 0
            return

        self.zoom -= 1

        self.zoom_camera()

    def zoom_camera(self) -> None:
        pass
        # TODO
        #  - find vector between Look At and Pos of camera
        #  - scale vector by zoom
        #  - reset pos based on Look At + vector
        #  - set look at back to the original look at
