from typing import Self

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.map import Map
from f1p.ui.components.menu import Menu
from f1p.ui.components.origin import Origin


class F1PlayerApp(ShowBase):
    def __init__(self, width: int = 800, height: int = 800, draw_origin: bool = False):
        super().__init__(self)

        self.width = width
        self.height = height

        self._data_extractor: DataExtractorService | None = None
        self.cam.setPos(0, -70, 40)
        self.cam.lookAt(0, 0, 0)

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
        menu = Menu(self.pixel2d, self.width, 40, self.data_extractor)
        menu.render()

        return self

    def register_map(self) -> Self:
        map = Map(self.render, self.data_extractor)

        return self

app = F1PlayerApp(draw_origin=True)
# app.disableMouse()  # disable camera controls
(
    app.configure_window()
    .draw_menu()
    .register_map()
    .run()
)
