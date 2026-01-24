from typing import Any

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager, Task
from panda3d.core import StaticTextFont, Point3, TextNode

from f1p.services.data_extractor.service import DataExtractorService


class WeatherBoard(DirectObject):
    def __init__(
        self,
        pixel2d,
        task_manager: TaskManager,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        window_width: int,
        data_extractor: DataExtractorService,
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.task_manager = task_manager
        self.width = 150
        self.height = 275
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.window_width = window_width
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render_weather_board)

        self.frame: DirectFrame | None = None
        self.title_frame: DirectFrame | None = None
        self.title: OnscreenText | None = None
        self.title_2: OnscreenText | None = None
        self.condition: OnscreenText | None = None
        self.temperature_C: OnscreenText | None = None
        self.temperature_F: OnscreenText | None = None
        self.track_temp_title: OnscreenText | None = None
        self.track_temp_C: OnscreenText | None = None
        self.track_temp_F: OnscreenText | None = None
        self.humidity_title: OnscreenText | None = None
        self.humidity: OnscreenText | None = None

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0.20, 0.20, 0.20, 0.7),
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(self.window_width - self.width - 10, 0, -50),
        )

    def render_title(self) -> None:
        self.title_frame = DirectFrame(
            parent=self.frame,
            frameColor=(0.15, 0.15, 0.15, 0.7),
            frameSize=(0, self.width, 0, -45),
            pos=Point3(0, 0, 0),
        )

        self.title = OnscreenText(
            parent=self.title_frame,
            pos=(self.width / 2, -18),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text="WEATHER",
        )

        self.title_2 = OnscreenText(
            parent=self.title_frame,
            pos=(self.width / 2, -35),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text="CONDITIONS",
        )

    def render_weather(self) -> None:
        self.condition = OnscreenText(
            parent=self.frame,
            pos=(5, -65),
            scale=self.width / 8,
            fg=(0.8, 1, 0, 0.7),
            font=self.text_font,
            align=TextNode.A_left,
            text="RAIN",
        )

        self.temperature_C = OnscreenText(
            parent=self.frame,
            pos=(5, -85),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="15°C",
        )

        self.temperature_F = OnscreenText(
            parent=self.frame,
            pos=(50, -85),
            scale=self.width / 10,
            fg=(0.5, 0.5, 0.5, 1),
            font=self.text_font,
            align=TextNode.A_left,
            text="59°F",
        )

    def render_track_temperature(self) -> None:
        self.track_temp_title = OnscreenText(
            parent=self.frame,
            pos=(5, -105),
            scale=self.width / 13,
            fg=(0.8, 1, 0, 0.7),
            font=self.text_font,
            align=TextNode.A_left,
            text="TRACK TEMP",
        )

        self.track_temp_C = OnscreenText(
            parent=self.frame,
            pos=(5, -125),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="17°C",
        )

        self.track_temp_F = OnscreenText(
            parent=self.frame,
            pos=(50, -125),
            scale=self.width / 10,
            fg=(0.5, 0.5, 0.5, 1),
            font=self.text_font,
            align=TextNode.A_left,
            text="62°F",
        )

    def render_humidity(self) -> None:
        self.humidity_title = OnscreenText(
            parent=self.frame,
            pos=(5, -145),
            scale=self.width / 13,
            fg=(0.8, 1, 0, 0.7),
            font=self.text_font,
            align=TextNode.A_left,
            text="HUMIDITY",
        )

        self.humidity = OnscreenText(
            parent=self.frame,
            pos=(5, -165),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="54%",
        )

    def render_pressure(self) -> None:
        self.pressure_title = OnscreenText(
            parent=self.frame,
            pos=(5, -185),
            scale=self.width / 13,
            fg=(0.8, 1, 0, 0.7),
            font=self.text_font,
            align=TextNode.A_left,
            text="AIR PRESSURE",
        )

        self.pressure = OnscreenText(
            parent=self.frame,
            pos=(5, -205),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="101.325 kPa",
        )

    def render_wind(self) -> None:
        self.wind_title = OnscreenText(
            parent=self.frame,
            pos=(5, -225),
            scale=self.width / 13,
            fg=(0.8, 1, 0, 0.7),
            font=self.text_font,
            align=TextNode.A_left,
            text="AIR PRESSURE",
        )

        self.wind_speed = OnscreenText(
            parent=self.frame,
            pos=(5, -245),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="5.7 km/h",
        )

        self.wind_direction = OnscreenText(
            parent=self.frame,
            pos=(5, -265),
            scale=self.width / 13,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="NORTH EAST",
        )

    def render_weather_board(self) -> None:
        self.task_manager.add(self.render, "renderLeaderboard")

    def render(self, task: Task) -> Any:
        self.render_frame()
        self.render_title()
        self.render_weather() # TODO is raining
        self.render_track_temperature()
        self.render_humidity()
        self.render_pressure()
        self.render_wind()

        return task.done