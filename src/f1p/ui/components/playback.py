import math
from datetime import timedelta, datetime
from math import sin, cos

from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.gui.DirectSlider import DirectSlider
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.Task import TaskManager
from panda3d.core import Point3, StaticTextFont, Camera, deg2Rad, TextNode
from pandas import Timedelta

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.gui.button import BlackButton
from f1p.ui.components.gui.drop_down import BlackDropDown
from f1p.ui.components.leaderboard import Leaderboard
from f1p.ui.components.map import Map


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
        circuit_map: Map,
        leaderboard: Leaderboard,
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
        self.circuit_map = circuit_map
        self.leaderboard = leaderboard
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render)

        self.frame: DirectFrame | None = None
        self.play_button: DirectButton | None = None
        self.timeline: DirectSlider | None = None
        self.playback_speed_button: DirectOptionMenu | None = None
        self.camera_button: DirectOptionMenu | None = None

        self.orbiting_camera: bool = True
        self.playing: bool = False
        self.playback_speed: float = 1.0

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.18, 0.18, 0.18, 1),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(0, 0, self.height - self.window_height)
        )

    def move_timeline(self, task):
        if not self.playing:
            return task.cont

        # fps = globalClock.getAverageFrameRate()
        # spf = 1 / fps
        # current_value = self.timeline["value"]
        # new_value = current_value + (spf * 1000 * self.playback_speed)

        current_value = self.timeline["value"]
        new_value = current_value + self.playback_speed

        if new_value > self.timeline["range"][1]:
            self.playing = False
            return task.cont

        self.timeline["value"] = new_value

        return task.cont

    def play_pause(self) -> None:
        if not self.playing:
            self.playing = True
        else:
            self.playing = False

    def render_play_button(self) -> None:
        self.play_button = BlackButton(
            parent=self.frame,
            frameSize=(-17, 17, -self.height / 2, self.height / 2),
            command=self.play_pause,
            text_font=self.symbols_font,
            text="⏯",
            text_scale=self.height - 5,
            text_align=TextNode.ACenter,
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(17, 0, -self.height / 2)
        )

    def update_components(self) -> None:
        session_time_tick = int(self.timeline["value"])
        messenger.send("updateDrivers", sentArgs=[session_time_tick])
        messenger.send("updateLeaderboard", sentArgs=[session_time_tick])

    def render_timeline(self) -> None:
        self.timeline = DirectSlider(
            parent=self.frame,
            value=1,
            range=(1, self.data_extractor.session_ticks),
            pageSize=1,
            frameSize=(0, self.width - 121, -self.height / 2, self.height / 2),
            frameColor=(0.15, 0.15, 0.15, 1),
            thumb_frameSize=(0, 5, -self.height / 2, self.height / 2),
            thumb_frameColor=(0.1, 0.1, 0.1, 1),
            command=self.update_components,
            text_font=self.text_font,
            text_scale=self.height,
            text_fg=(1, 1, 1, 1),
            text_pos=(-2, (-self.height / 2) + 7),
            pos=Point3(34, 0, -self.height / 2)
        )

    def change_playback_speed(self, playback_speed: str) -> None:
        match playback_speed:
            case "x10":
                self.playback_speed = 1.0
            case "x20":
                self.playback_speed = 2.0
            case "x30":
                self.playback_speed = 3.0
            case "x40":
                self.playback_speed = 4.0
            case "x50":
                self.playback_speed = 5.0

    def render_playback_speed_button(self) -> None:
        self.playback_speed_button = BlackDropDown(
            parent=self.frame,
            width=47,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 15,
            popup_menu_below=False,
            command=self.change_playback_speed,
            text="speed",
            text_pos=(23.5, (-self.height / 2) + 10),
            text_align=TextNode.ACenter,
            item_text_align=TextNode.ACenter,
            items=["x10", "x20", "x30", "x40", "x50"],
            item_scale=1.0,
            initialitem=0,
            pos=Point3(self.width - 87, 0, -self.height / 2)
        )

    def move_camera(self, task):
        if not self.orbiting_camera:
            return task.cont

        current_x = self.camera.getX()
        current_y = self.camera.getY()

        rad = deg2Rad(0.3)

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
            item_text_align=TextNode.ACenter,
            items=["🌎", "🗺"],
            item_scale=1.0,
            initialitem=0,
            pos=Point3(self.width - 40, 0, -self.height / 2)
        )

    def render(self):
        self.task_manager.add(self.move_camera, "move_camera")
        self.task_manager.add(self.move_timeline, "move_timeline")
        self.render_frame()
        self.render_play_button()
        self.render_timeline()
        self.render_playback_speed_button()
        self.render_camera_button()
