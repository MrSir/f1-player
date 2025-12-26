from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from panda3d.core import StaticTextFont, Point3, Loader, TransparencyAttrib, TextNode

from f1p.services.data_extractor import DataExtractorService
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
        self.width = 200
        self._height: float | None = None
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.circuit_map = circuit_map
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render)

        self.frame: DirectFrame | None = None
        self.f1_logo: OnscreenImage | None = None
        self.lap_counter: DirectLabel | None = None
        self.team_colors: list[DirectFrame] = []
        self.driver_abbreviations: list[DirectLabel] = []
        self.driver_times: list[DirectLabel] = []
        self.driver_tires: list[DirectLabel] = []

    @property
    def height(self) -> float:
        if self._height is None:
            self._height = 25 + 50 + (len(self.circuit_map.drivers) * 23)

        return self._height

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
            text='LAP 1/57',  # TODO grab actual laps and lap count
        )

    def render_drivers(self) -> None:
        for index, driver in enumerate(self.circuit_map.drivers):
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
                    text="Interval" if index == 0 else "+12.250", # TODO compute actual intervals
                )
            )

            self.driver_tires.append(
                DirectLabel(
                    parent=self.frame,
                    pos=Point3(185, 0, -85 - (index * 23)),
                    scale=self.width / 14,
                    frameColor=(0, 0, 0, 0),
                    text_fg=(1, 0, 0, 0.8), # TODO compute tire color
                    text_font=self.text_font,
                    text="S", # TODO compute actual tire compound
                )
            )

    def update(self) -> None:
        # TODO implement appropriate updates
        pass

    def render(self) -> None:
        self.render_frame()
        self.render_f1_logo()
        self.render_lap_counter()
        self.render_drivers()
