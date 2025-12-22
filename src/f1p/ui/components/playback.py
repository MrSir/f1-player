from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import RAISED, TEXT_SORT_INDEX
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from panda3d.core import Point3, StaticTextFont

from f1p.services.data_extractor import DataExtractorService


class PlaybackControls(DirectObject):
    def __init__(
        self,
        pixel2d,
        window_height: int,
        width: int,
        height: int,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        data_extractor: DataExtractorService
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.window_height = window_height
        self.width = width
        self.height = height
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render)

        self.frame: DirectFrame | None = None
        self.play_button: DirectButton | None = None
        self.timeline: DirectSlider | None = None
        self.playback_speed_button: DirectOptionMenu | None = None
        self.camera_button: DirectOptionMenu | None = None

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0, 0, 0, 0.6),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(0, 0, self.height - self.window_height)
        )

    def render_play_button(self) -> None:
        self.play_button = DirectButton(
            parent=self.frame,
            frameSize=(-17, 17, -self.height / 2, self.height / 2),
            frameColor=(0.1, 0.1, 0.1, 1),
            relief=RAISED,
            borderWidth=(2, 2),
            command=None,  # TODO
            pressEffect=1,
            text_font=self.symbols_font,
            text="⏯",
            text_scale=self.height,
            text_fg=(1, 1, 1, 1),
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(17, 0, -self.height / 2)
        )

    def render_timeline(self) -> None:
        self.timeline = DirectSlider(
            parent=self.frame,
            value=0,  # TODO
            range=(0, 100),  # TODO
            pageSize=1,  # TODO
            frameSize=(0, self.width - 129, -self.height / 2, self.height / 2),
            frameColor=(0.1, 0.1, 0.1, 1),
            thumb_frameSize=(0, 5, -self.height / 2, self.height / 2),
            thumb_frameColor=(0.05, 0.05, 0.05, 1),
            command=None,  # TODO
            text_font=self.text_font,
            text_scale=self.height,
            text_fg=(1, 1, 1, 1),
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(34, 0, -self.height / 2)
        )

    def render_playback_speed_button(self) -> None:
        self.playback_speed_button = DirectOptionMenu(
            parent=self.frame,
            frameSize=(0, 65, -self.height / 2, self.height / 2),
            frameColor=(0.1, 0.1, 0.1, 1),
            relief=RAISED,
            borderWidth=(3, 3),
            command=None,  # TODO
            pressEffect=1,
            text="speed",
            text_font=self.text_font,
            text_scale=self.height - 7,
            text_fg=(1, 1, 1, 1),
            text_pos=(5, (-self.height / 2) + 8),
            items=["x0.5", "x1.0", "x1.5", "x2.0"],
            initialitem=1,
            item_text_scale=self.height - 7,
            pos=Point3(self.width - 95, 0, -self.height / 2)
        )

    def render_camera_button(self) -> None:
        self.camera_button = DirectOptionMenu(
            parent=self.frame,
            frameSize=(0, 30, -self.height / 2, self.height / 2),
            frameColor=(0.1, 0.1, 0.1, 1),
            relief=RAISED,
            borderWidth=(3, 3),
            command=None,
            pressEffect=1,
            text="camera",
            text_font=self.symbols_font,
            text_scale=self.height - 10,
            text_fg=(1, 1, 1, 1),
            text_pos=(5, (-self.height / 2) + 8),
            items=["📹", "🖑"],
            initialitem=0,
            item_text_scale=self.height - 10,
            item_text_font=self.symbols_font,
            pos=Point3(self.width - 30, 0, -self.height / 2)
        )

    def render(self):
        self.render_frame()
        self.render_play_button()
        self.render_timeline()
        self.render_playback_speed_button()
        self.render_camera_button()
