from typing import Any

from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import Task, TaskManager
from panda3d.core import Point3, StaticTextFont, TextNode

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
        self.accept("updateWeather", self.update)

        self.frame: DirectFrame | None = None
        self.title_frame: DirectFrame | None = None
        self.title: OnscreenText | None = None
        self.title_2: OnscreenText | None = None
        self.weather_symbol: OnscreenText | None = None
        self.weather_text: OnscreenText | None = None
        self.temperature_C: OnscreenText | None = None
        self.temperature_F: OnscreenText | None = None
        self.track_temp_title: OnscreenText | None = None
        self.track_temp_symbol: OnscreenText | None = None
        self.track_temp_C: OnscreenText | None = None
        self.track_temp_F: OnscreenText | None = None
        self.humidity_title: OnscreenText | None = None
        self.humidity_symbol: OnscreenText | None = None
        self.humidity: OnscreenText | None = None
        self.pressure_title: OnscreenText | None = None
        self.pressure: OnscreenText | None = None
        self.wind_title: OnscreenText | None = None
        self.wind_direction: OnscreenText | None = None
        self.wind_speed: OnscreenText | None = None
        self.wind_direction_text: OnscreenText | None = None

        self.highlighter_yellow_color = (0.8, 1, 0, 1)

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
        self.weather_symbol = OnscreenText(
            parent=self.frame,
            pos=(5, -64),
            scale=self.width / 7,
            fg=self.highlighter_yellow_color,
            font=self.symbols_font,
            align=TextNode.A_left,
            text="🌣",
        )

        self.weather_text = OnscreenText(
            parent=self.frame,
            pos=(30, -65),
            scale=self.width / 8,
            fg=self.highlighter_yellow_color,
            font=self.text_font,
            align=TextNode.A_left,
            text="WEATHER",
        )

        self.temperature_C = OnscreenText(
            parent=self.frame,
            pos=(5, -85),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0°C",
        )

        self.temperature_F = OnscreenText(
            parent=self.frame,
            pos=(70, -85),
            scale=self.width / 10,
            fg=(0.5, 0.5, 0.5, 1),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0°F",
        )

    def render_track_temperature(self) -> None:
        self.track_temp_title = OnscreenText(
            parent=self.frame,
            pos=(5, -105),
            scale=self.width / 13,
            fg=self.highlighter_yellow_color,
            font=self.text_font,
            align=TextNode.A_left,
            text="TRACK TEMP",
        )

        self.track_temp_symbol = OnscreenText(
            parent=self.frame,
            pos=(5, -125),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.symbols_font,
            align=TextNode.A_left,
            text="🌡",
        )

        self.track_temp_C = OnscreenText(
            parent=self.frame,
            pos=(20, -125),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0°C",
        )

        self.track_temp_F = OnscreenText(
            parent=self.frame,
            pos=(80, -125),
            scale=self.width / 10,
            fg=(0.5, 0.5, 0.5, 1),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0°F",
        )

    def render_humidity(self) -> None:
        self.humidity_title = OnscreenText(
            parent=self.frame,
            pos=(5, -145),
            scale=self.width / 13,
            fg=self.highlighter_yellow_color,
            font=self.text_font,
            align=TextNode.A_left,
            text="HUMIDITY",
        )

        self.humidity_symbol = OnscreenText(
            parent=self.frame,
            pos=(5, -165),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.symbols_font,
            align=TextNode.A_left,
            text="🌢",
        )

        self.humidity = OnscreenText(
            parent=self.frame,
            pos=(20, -165),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0%",
        )

    def render_pressure(self) -> None:
        self.pressure_title = OnscreenText(
            parent=self.frame,
            pos=(5, -185),
            scale=self.width / 13,
            fg=self.highlighter_yellow_color,
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
            text="000.00 kPa",
        )

    def render_wind(self) -> None:
        self.wind_title = OnscreenText(
            parent=self.frame,
            pos=(5, -225),
            scale=self.width / 13,
            fg=self.highlighter_yellow_color,
            font=self.text_font,
            align=TextNode.A_left,
            text="WIND",
        )

        self.wind_direction = OnscreenText(
            parent=self.frame,
            pos=(5, -245),
            scale=self.width / 8,
            fg=(1, 1, 1, 0.8),
            font=self.symbols_font,
            align=TextNode.A_left,
            text="🡿",
        )

        self.wind_speed = OnscreenText(
            parent=self.frame,
            pos=(20, -245),
            scale=self.width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="00.0 km/h",
        )

        self.wind_direction_text = OnscreenText(
            parent=self.frame,
            pos=(5, -265),
            scale=self.width / 13,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            align=TextNode.A_left,
            text="Pending...",
        )

    def render_weather_board(self) -> None:
        self.task_manager.add(self.render, "renderLeaderboard")

    def render(self, task: Task) -> Any:
        self.render_frame()
        self.render_title()
        self.render_weather()
        self.render_track_temperature()
        self.render_humidity()
        self.render_pressure()
        self.render_wind()

        return task.done

    def update(self, session_time_tick: int) -> None:
        weather_data = self.data_extractor.get_current_weather_data(session_time_tick)

        if weather_data is None:
            return

        if self.weather_symbol["text"] != weather_data["WeatherSymbol"]:
            self.weather_symbol["text"] = weather_data["WeatherSymbol"]
        if self.weather_text["text"] != weather_data["WeatherText"]:
            self.weather_text["text"] = weather_data["WeatherText"]

        temp_C = f"{weather_data['AirTemp']:.1f}°C"
        temp_F = f"{weather_data['AirTempF']:.1f}°F"
        if self.temperature_C["text"] != temp_C:
            self.temperature_C["text"] = temp_C
        if self.temperature_F["text"] != temp_F:
            self.temperature_F["text"] = temp_F

        track_temp_C = f"{weather_data['TrackTemp']:.1f}°C"
        track_temp_F = f"{weather_data['TrackTempF']:.1f}°F"
        if self.track_temp_C["text"] != track_temp_C:
            self.track_temp_C["text"] = track_temp_C
        if self.track_temp_F["text"] != track_temp_F:
            self.track_temp_F["text"] = track_temp_F

        humidity = f"{weather_data['Humidity']:.0f}%"
        if self.humidity["text"] != humidity:
            self.humidity["text"] = humidity

        pressure = f"{weather_data['Pressure']:.2f} kPa"
        if self.pressure["text"] != pressure:
            self.pressure["text"] = pressure

        if self.wind_direction["text"] != weather_data["WindDirectionSymbol"]:
            self.wind_direction["text"] = weather_data["WindDirectionSymbol"]
        if self.wind_direction_text["text"] != weather_data["WindDirectionText"]:
            self.wind_direction_text["text"] = weather_data["WindDirectionText"]
        wind_speed = f"{weather_data['WindSpeed']:.2f} km/h"
        if self.wind_speed["text"] != wind_speed:
            self.wind_speed["text"] = wind_speed
