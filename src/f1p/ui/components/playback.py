import math
from math import sin, cos

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager
from panda3d.core import Point3, StaticTextFont, Camera, deg2Rad, TextNode

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
            text_scale=self.height - 5,
            text_align=TextNode.ACenter,
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(17, 0, -self.height / 2)
        )

    def render_timeline(self) -> None:
        self.timeline = DirectSlider(
            parent=self.frame,
            value=0,  # TODO
            range=(0, 100),  # TODO
            pageSize=1,  # TODO
            frameSize=(0, self.width - 121, -self.height / 2, self.height / 2),
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
            width=47,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 15,
            popup_menu_below=False,
            command=None,  # TODO
            text="speed",
            text_pos=(23.5, (-self.height / 2) + 10),
            text_align=TextNode.ACenter,
            item_text_pos=(23.5, (-self.height / 2) + 10),
            item_text_align=TextNode.ACenter,
            items=["x1.0", "x2.0"],
            initialitem=0,
            pos=Point3(self.width - 87, 0, -self.height / 2)
        )

    def move_camera(self, task):
        if not self.orbiting_camera:
            return task.cont

        current_x = self.camera.getX()
        current_y = self.camera.getY()

        rad = deg2Rad(0.1)

        self.camera.setX((current_x * cos(rad)) - (current_y * sin(rad)))
        self.camera.setY((current_x * sin(rad)) + (current_y * cos(rad)))

        self.camera.lookAt(0, 0, 0)

        return task.cont

    def switch_camera(self, item: str) -> None:
        match item:
            case "🌎":
                self.camera.setPos(0, -70, 40)
                self.camera.lookAt(0, 0, 0)

                self.orbiting_camera = True
            case "🗺":
                self.camera.setPos(0, 0, 100)
                self.camera.lookAt(0, 0, 0)

                self.orbiting_camera = False

    def render_camera_button(self) -> None:
        self.camera_button = BlackDropDown(
            parent=self.frame,
            width=40,
            height=self.height,
            font=self.symbols_font,
            font_scale=self.height - 10,
            popup_menu_below=False,
            command=self.switch_camera,
            text="camera",
            text_pos=(20, (-self.height / 2) + 10),
            text_align=TextNode.ACenter,
            item_text_pos=(20, (-self.height / 2) + 10),
            item_text_align=TextNode.ACenter,
            items=["🌎", "🗺"],
            initialitem=0,
            pos=Point3(self.width - 40, 0, -self.height / 2)
        )

    def render(self):
        self.task_manager.add(self.move_camera, "move_camera")
        self.render_frame()
        self.render_play_button()
        self.render_timeline()
        self.render_playback_speed_button()
        self.render_camera_button()
