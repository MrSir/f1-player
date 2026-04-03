from typing import Self

import numpy as np
import pandas as pd
from fastf1.core import Session
from pandas import DataFrame, Series, Timedelta

from f1p.utils.dataframe import merge_in_session_time_ticks


class WeatherParser:
    def __init__(self, session: Session) -> None:
        self.session: Session = session

        self._weather_data: DataFrame | None = None
        self._processed_weather_data: DataFrame | None = None

    @property
    def weather_data(self) -> DataFrame:
        if self._weather_data is None:
            self._weather_data = self.session.weather_data

        return self._weather_data

    @property
    def processed_weather_data(self) -> DataFrame:
        if self._processed_weather_data is None:
            raise ValueError("Weather data is not processed yet.")

        return self._processed_weather_data

    def _trim_to_session_time(
        self,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> Self:
        df = self.weather_data.copy()
        df = df[df["Time"] >= session_start_time]
        df = df[df["Time"] <= session_end_time]

        self._processed_weather_data = df.reset_index(drop=True)

        return self

    def _add_session_time_ticks(self, session_time_ticks_df: DataFrame) -> Self:
        df = merge_in_session_time_ticks(
            self._processed_weather_data,
            session_time_ticks_df,
            target_df_comparison_column="Time",
        )

        self._processed_weather_data = df

        return self

    def _convert_air_temp_to_fahrenheit(self) -> Self:
        df = self._processed_weather_data.copy()

        df["AirTempF"] = (df["AirTemp"] * 9 / 5) + 32

        self._processed_weather_data = df

        return self

    def _convert_track_temp_to_fahrenheit(self) -> Self:
        df = self._processed_weather_data.copy()

        df["TrackTempF"] = (df["TrackTemp"] * 9 / 5) + 32

        self._processed_weather_data = df

        return self

    def _convert_pressure_to_kilopascal(self) -> Self:
        df = self._processed_weather_data.copy()

        df["Pressure"] = df["Pressure"] / 10

        self._processed_weather_data = df

        return self

    def _convert_wind_speed_to_km_p_h(self) -> Self:
        df = self._processed_weather_data.copy()

        df["WindSpeed"] = df["WindSpeed"] * 18 / 5

        self._processed_weather_data = df

        return self

    def _add_weather_symbol(self) -> Self:
        df = self._processed_weather_data.copy()

        df.loc[df["Rainfall"], "WeatherSymbol"] = "🌧"
        df["WeatherSymbol"] = df["WeatherSymbol"].fillna("🌣")

        self._processed_weather_data = df

        return self

    def _add_weather_text(self) -> Self:
        df = self._processed_weather_data.copy()

        df.loc[df["Rainfall"], "WeatherText"] = "RAIN"
        df["WeatherText"] = df["WeatherText"].fillna("SUNNY")

        self._processed_weather_data = df

        return self

    def _add_wind_direction_symbol(self) -> Self:
        df = self._processed_weather_data.copy()

        df["WindDirectionSymbol"] = np.select(
            [
                ((df["WindDirection"] > 337.5) | (df["WindDirection"] <= 22.5)),
                ((df["WindDirection"] > 22.5) & (df["WindDirection"] <= 67.5)),
                ((df["WindDirection"] > 67.5) & (df["WindDirection"] <= 112.5)),
                ((df["WindDirection"] > 112.5) & (df["WindDirection"] <= 157.5)),
                ((df["WindDirection"] > 157.5) & (df["WindDirection"] <= 202.5)),
                ((df["WindDirection"] > 202.5) & (df["WindDirection"] <= 247.5)),
                ((df["WindDirection"] > 247.5) & (df["WindDirection"] <= 292.5)),
                ((df["WindDirection"] > 292.5) & (df["WindDirection"] <= 337.5)),
            ],
            ["🢃", "🢇", "🢀", "🢄", "🢁", "🢅", "🢂", "🢆"],
            pd.NA,
        )
        df["WindDirectionSymbol"] = df["WindDirectionSymbol"].ffill()

        self._processed_weather_data = df

        return self

    def _add_wind_direction_text(self) -> Self:
        df = self._processed_weather_data.copy()

        df["WindDirectionText"] = np.select(
            [
                ((df["WindDirection"] > 337.5) | (df["WindDirection"] <= 22.5)),
                ((df["WindDirection"] > 22.5) & (df["WindDirection"] <= 67.5)),
                ((df["WindDirection"] > 67.5) & (df["WindDirection"] <= 112.5)),
                ((df["WindDirection"] > 112.5) & (df["WindDirection"] <= 157.5)),
                ((df["WindDirection"] > 157.5) & (df["WindDirection"] <= 202.5)),
                ((df["WindDirection"] > 202.5) & (df["WindDirection"] <= 247.5)),
                ((df["WindDirection"] > 247.5) & (df["WindDirection"] <= 292.5)),
                ((df["WindDirection"] > 292.5) & (df["WindDirection"] <= 337.5)),
            ],
            ["NORTH", "NORTH EAST", "EAST", "SOUTH EAST", "SOUTH", "SOUTH WEST", "WEST", "NORTH WEST"],
            pd.NA,
        )
        df["WindDirectionText"] = df["WindDirectionText"].ffill()

        self._processed_weather_data = df

        return self

    def parse(
        self,
        session_time_ticks_df: DataFrame,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> None:
        (
            self._trim_to_session_time(session_start_time, session_end_time)
            ._add_session_time_ticks(session_time_ticks_df)
            ._convert_air_temp_to_fahrenheit()
            ._convert_track_temp_to_fahrenheit()
            ._convert_pressure_to_kilopascal()
            ._convert_wind_speed_to_km_p_h()
            ._add_weather_symbol()
            ._add_weather_text()
            ._add_wind_direction_symbol()
            ._add_wind_direction_text()
        )

    def get_current_weather_data(self, session_time_tick: int) -> Series | None:
        df = self.processed_weather_data

        df = df[df["SessionTimeTick"] <= session_time_tick]
        df = df.sort_values(by="SessionTimeTick", ascending=False)

        if df.empty:
            return None

        return df.iloc[0]
