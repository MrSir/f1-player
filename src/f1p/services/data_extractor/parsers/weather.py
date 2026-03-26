from fastf1.core import Session
from pandas import DataFrame, Timedelta, Series


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

    def process_weather_data(
        self,
        processed_pos_data: DataFrame,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> None:
        df = processed_pos_data.copy()
        df = df[["SessionTimeTick", "SessionTime"]].drop_duplicates(keep="first").copy()

        weather_df = self.weather_data.copy()
        weather_df = weather_df[weather_df["Time"] >= session_start_time]
        weather_df = weather_df[weather_df["Time"] <= session_end_time]

        for record in weather_df.itertuples():
            weather_df.loc[weather_df["Time"] == record.Time, "SessionTimeTick"] = df.loc[
                df["SessionTime"] <= record.Time,
                "SessionTimeTick",
            ].max()

        weather_df["SessionTimeTick"] = weather_df["SessionTimeTick"].astype("int64")
        weather_df["AirTempF"] = (weather_df["AirTemp"] * 9 / 5) + 32
        weather_df["TrackTempF"] = (weather_df["TrackTemp"] * 9 / 5) + 32
        weather_df["Pressure"] = weather_df["Pressure"] / 10
        weather_df["WindSpeed"] = weather_df["WindSpeed"] * 18 / 5
        weather_df.loc[weather_df["Rainfall"], "WeatherSymbol"] = "🌧"
        weather_df.loc[weather_df["Rainfall"], "WeatherText"] = "RAIN"
        weather_df["WeatherSymbol"] = weather_df["WeatherSymbol"].fillna("🌣")
        weather_df["WeatherText"] = weather_df["WeatherText"].fillna("SUNNY")

        weather_df.loc[
            (weather_df["WindDirection"] > 337.5) | (weather_df["WindDirection"] <= 22.5),
            "WindDirectionSymbol",
        ] = "🢃"
        weather_df.loc[
            (weather_df["WindDirection"] > 337.5) | (weather_df["WindDirection"] <= 22.5),
            "WindDirectionText",
        ] = "NORTH"
        weather_df.loc[
            (weather_df["WindDirection"] > 22.5) & (weather_df["WindDirection"] <= 67.5),
            "WindDirectionSymbol",
        ] = "🢇"
        weather_df.loc[
            (weather_df["WindDirection"] > 22.5) & (weather_df["WindDirection"] <= 67.5),
            "WindDirectionText",
        ] = "NORTH EAST"
        weather_df.loc[
            (weather_df["WindDirection"] > 67.5) & (weather_df["WindDirection"] <= 112.5),
            "WindDirectionSymbol",
        ] = "🢀"
        weather_df.loc[
            (weather_df["WindDirection"] > 67.5) & (weather_df["WindDirection"] <= 112.5),
            "WindDirectionText",
        ] = "EAST"
        weather_df.loc[
            (weather_df["WindDirection"] > 112.5) & (weather_df["WindDirection"] <= 157.5),
            "WindDirectionSymbol",
        ] = "🢄"
        weather_df.loc[
            (weather_df["WindDirection"] > 112.5) & (weather_df["WindDirection"] <= 157.5),
            "WindDirectionText",
        ] = "SOUTH EAST"
        weather_df.loc[
            (weather_df["WindDirection"] > 157.5) & (weather_df["WindDirection"] <= 202.5),
            "WindDirectionSymbol",
        ] = "🢁"
        weather_df.loc[
            (weather_df["WindDirection"] > 157.5) & (weather_df["WindDirection"] <= 202.5),
            "WindDirectionText",
        ] = "SOUTH"
        weather_df.loc[
            (weather_df["WindDirection"] > 202.5) & (weather_df["WindDirection"] <= 247.5),
            "WindDirectionSymbol",
        ] = "🢅"
        weather_df.loc[
            (weather_df["WindDirection"] > 202.5) & (weather_df["WindDirection"] <= 247.5),
            "WindDirectionText",
        ] = "SOUTH WEST"
        weather_df.loc[
            (weather_df["WindDirection"] > 247.5) & (weather_df["WindDirection"] <= 292.5),
            "WindDirectionSymbol",
        ] = "🢂"
        weather_df.loc[
            (weather_df["WindDirection"] > 247.5) & (weather_df["WindDirection"] <= 292.5),
            "WindDirectionText",
        ] = "WEST"
        weather_df.loc[
            (weather_df["WindDirection"] > 292.5) & (weather_df["WindDirection"] <= 337.5),
            "WindDirectionSymbol",
        ] = "🢆"
        weather_df.loc[
            (weather_df["WindDirection"] > 292.5) & (weather_df["WindDirection"] <= 337.5),
            "WindDirectionText",
        ] = "NORTH WEST"

        weather_df["WindDirectionSymbol"] = weather_df["WindDirectionSymbol"].ffill()
        weather_df["WindDirectionText"] = weather_df["WindDirectionText"].ffill()

        self._processed_weather_data = weather_df

    def get_current_weather_data(self, session_time_tick: int) -> Series | None:
        weather_df = self.processed_weather_data

        weather_df = weather_df[weather_df["SessionTimeTick"] <= session_time_tick]
        weather_df = weather_df.sort_values(by="SessionTimeTick", ascending=False)

        if weather_df.empty:
            return None

        return weather_df.iloc[0]