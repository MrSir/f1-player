from typing import Self

from direct.showbase.ShowBase import ShowBase
from panda3d.core import PStatClient, StaticTextFont, WindowProperties

from f1p.services.data_extractor.parsers.session import SessionParser
from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.camera.component import MainCamera
from f1p.ui.components.leaderboard.component import Leaderboard
from f1p.ui.components.map import Map
from f1p.ui.components.menu import Menu
from f1p.ui.components.playback import PlaybackControls
from f1p.ui.components.weather import WeatherBoard


class F1PlayerApp(ShowBase):
    def __init__(
        self,
        width: int = 800,
        height: int = 800,
        show_frame_rate: bool = False,
        pstat_debug: bool = False,
    ):
        super().__init__(self)

        self.width = width
        self.height = height
        self.show_frame_rate = show_frame_rate
        self.pstat_debug = pstat_debug
        self.ui_components: list = []

        self._symbols_font: StaticTextFont | None = None
        self._text_font: StaticTextFont | None = None
        self._session_parser: SessionParser | None = None
        self._data_extractor: DataExtractorService | None = None

    @property
    def session_parser(self) -> SessionParser:
        if self._session_parser is None:
            self._session_parser = SessionParser()

        return self._session_parser

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

    @property
    def symbols_font(self) -> StaticTextFont:
        if self._symbols_font is None:
            self._symbols_font = self.loader.loadFont("./src/f1p/ui/fonts/NotoSansSymbols2-Regular.ttf")

        return self._symbols_font

    @property
    def text_font(self) -> StaticTextFont:
        if self._text_font is None:
            self._text_font = self.loader.loadFont("./src/f1p/ui/fonts/f1_font.ttf")

        return self._text_font

    def _configure_window(self) -> Self:
        props = WindowProperties()
        props.setSize(self.width, self.height)
        props.setFixedSize(True)
        props.setTitle("F1 Player")
        self.win.requestProperties(props)

        return self

    def _draw_menu(self) -> Self:
        menu = Menu(
            self.pixel2d,
            self.taskMgr,
            self.messenger,
            self.width,
            40,
            self.text_font,
            self.data_extractor,
            self.session_parser,
        )
        menu.render()

        return self

    def _register_ui_components(self) -> Self:
        playback_controls = PlaybackControls(
            self.pixel2d,
            self.taskMgr,
            self.height,
            self.width,
            30,
            self.symbols_font,
            self.text_font,
            self.data_extractor,
        )

        circuit_map = Map(self, self.data_extractor)

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

    def _register_controls(self) -> Self:
        controls = MainCamera(self.taskMgr, self.mouseWatcherNode, self.cam)
        controls.configure()

        return self

    def run(self) -> None:
        self.setBackgroundColor(0.3, 0.3, 0.3, 1)

        self.taskMgr.setupTaskChain("loadingData", numThreads=1)
        self.taskMgr.setupTaskChain("updating", numThreads=7)

        # Turn off default mouse camera controls
        self.disableMouse()

        self.setFrameRateMeter(self.show_frame_rate)

        if self.pstat_debug:
            PStatClient.connect()

        self._configure_window()._draw_menu()._register_ui_components()._register_controls()

        super().run()