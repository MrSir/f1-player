from pathlib import Path
from typing import Self

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.map import Map
from f1p.ui.components.menu import Menu
from f1p.ui.components.origin import Origin
from f1p.ui.components.playback import PlaybackControls


class F1PlayerApp(ShowBase):

    def __init__(self, width: int = 800, height: int = 800, draw_origin: bool = False):
        super().__init__(self)

        self.symbols_font = self.loader.loadFont("./src/f1p/ui/fonts/NotoSansSymbols2-Regular.ttf")
        self.text_font = self.loader.loadFont("./src/f1p/ui/fonts/RobotoMono-Bold.ttf")

        self.width = width
        self.height = height

        self._data_extractor: DataExtractorService | None = None
        self.cam.setPos(0, -70, 40)
        self.cam.lookAt(0, 0, 0)

        self.ui_components: list = []

        if draw_origin:
            origin = Origin(self.render)
            origin.render()

    @property
    def data_extractor(self) -> DataExtractorService:
        if self._data_extractor is None:
            self._data_extractor = DataExtractorService()

        return self._data_extractor

    def configure_window(self) -> Self:
        props = WindowProperties()
        props.setSize(self.width, self.height)
        self.win.requestProperties(props)

        return self

    def draw_menu(self) -> Self:
        menu = Menu(self.pixel2d, self.width, 40, self.text_font, self.data_extractor)
        menu.render()

        return self

    def register_ui_components(self) -> Self:
        self.ui_components = [
            Map(self.render, self.data_extractor),
            PlaybackControls(self.pixel2d, self.height, self.width, 30, self.symbols_font, self.text_font, self.data_extractor),
        ]

        return self

app = F1PlayerApp(draw_origin=True)
# app.disableMouse()  # disable camera controls
(
    app.configure_window()
    .draw_menu()
    .register_ui_components()
    .run()
)
