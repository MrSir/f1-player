import math
from math import sin, cos

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import RAISED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from panda3d.core import Point3, StaticTextFont, Camera

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.gui.button import BlackButton
from f1p.ui.components.gui.drop_down import BlackDropDown


class PlaybackControls(DirectObject):
    def __init__(
        self,
        pixel2d,
        camera: Camera,
        task_manager: TaskManager,
        window_height: int,
        width: int,
        height: int,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        data_extractor: DataExtractorService
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.camera = camera
        self.task_manager = task_manager
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

        self.orbiting_camera: bool = True


    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0, 0, 0, 0.6),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(0, 0, self.height - self.window_height)
        )

    def render_play_button(self) -> None:
        self.play_button = BlackButton(
            parent=self.frame,
            frameSize=(-17, 17, -self.height / 2, self.height / 2),
            command=None,  # TODO
            text_font=self.symbols_font,
            text="⏯",
            text_scale=self.height,
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(17, 0, -self.height / 2)
        )

    def render_timeline(self) -> None:
        self.timeline = DirectSlider(
            parent=self.frame,
            value=0,  # TODO
            range=(0, 100),  # TODO
            pageSize=1,  # TODO
            frameSize=(0, self.width - 131, -self.height / 2, self.height / 2),
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
        self.playback_speed_button = BlackDropDown(
            parent=self.frame,
            width=65,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 7,
            popup_menu_below=False,
            command=None,  # TODO
            text="speed",
            text_pos=(5, (-self.height / 2) + 8),
            item_text_pos=(5, (-self.height / 2) + 8),
            items=["x0.5", "x1.0", "x1.5", "x2.0"],
            initialitem=1,
            pos=Point3(self.width - 97, 0, -self.height / 2)
        )

    def move_camera(self, task):
        if not self.orbiting_camera:
            return task.cont

        current_x = self.camera.getX()
        current_y = self.camera.getY()

        deg = 0.25
        rad = deg * math.pi / 180

        self.camera.setX((current_x*cos(rad)) - (current_y * sin(rad)))
        self.camera.setY((current_x*sin(rad)) + (current_y * cos(rad)))

        self.camera.lookAt(0,0,0)

        return task.cont

    def switch_camera(self, item: str) -> None:
        match item:
            case "📹":
                self.orbiting_camera = True
            case "🖑":
                self.orbiting_camera = False

    def render_camera_button(self) -> None:
        self.camera_button = BlackDropDown(
            parent=self.frame,
            width=30,
            height=self.height,
            font=self.symbols_font,
            font_scale= self.height -10,
            popup_menu_below=False,
            command=self.switch_camera,
            text="camera",
            text_pos=(5, (-self.height / 2) + 8),
            item_text_pos=(5, (-self.height / 2) + 8),
            items=["📹", "🖑"],
            initialitem=0,
            pos=Point3(self.width - 30, 0, -self.height / 2)
        )

    def render(self):
        self.task_manager.add(self.move_camera, "move_camera")
        self.render_frame()
        self.render_play_button()
        self.render_timeline()
        self.render_playback_speed_button()
        self.render_camera_button()
