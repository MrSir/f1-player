from typing import Self

from direct.showbase.ShowBase import ShowBase
from panda3d.core import WindowProperties

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.menu import Menu


class F1PlayerApp(ShowBase):
    def __init__(self, width: int = 800, height: int = 800):
        super().__init__(self)

        self.width = width
        self.height = height

        self._data_extractor: DataExtractorService | None = None

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


app = F1PlayerApp()
app.disableMouse()  # disable camera controls
(
    app.configure_window()
    .draw_menu()
    .run()
)
