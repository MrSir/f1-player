import math
from pathlib import Path
from typing import Any, Self

import fastf1
import numpy as np
import pandas as pd
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.showbase.MessengerGlobal import messenger
from direct.task.Task import Task, TaskManager
from fastf1.core import Session, Telemetry
from panda3d.core import LVecBase4f, NodePath, Point3, StaticTextFont
from pandas import DataFrame, Series, Timedelta

from f1p.services.data_extractor.parsers.laps import LapsParser
from f1p.services.data_extractor.parsers.position import PositionParser
from f1p.services.data_extractor.parsers.session import SessionParser
from f1p.services.data_extractor.parsers.telemetry import TelemetryParser
from f1p.services.data_extractor.parsers.track import TrackParser
from f1p.services.data_extractor.parsers.weather import WeatherParser
from f1p.utils.geometry import center_pos_data, find_center, resize_pos_data
from f1p.utils.timedelta import td_series_to_min_n_sec


class DataExtractorService(DirectObject):
    cache_path: Path = Path(__file__).parent.parent.parent.parent.parent / ".fastf1-cache"

    def __init__(
        self,
        parent: NodePath,
        task_manager: TaskManager,
        window_width: int,
        window_height: int,
        text_font: StaticTextFont,
    ):
        super().__init__()

        self.parent = parent
        self.task_manager = task_manager
        self.window_width = window_width
        self.window_height = window_height
        self.text_font = text_font

        self.session_parser: SessionParser | None = None
        self._session_results: DataFrame | None = None

        self._track_parser: TrackParser | None = None
        self._processed_corners: DataFrame | None = None
        self._track_statuses: DataFrame | None = None

        self._weather_parser: WeatherParser | None = None
        self._laps_parser: LapsParser | None = None
        self._pos_parser: PositionParser | None = None
        self._telemetry_parser: TelemetryParser | None = None

        self.data: DataFrame | None = None

        self._session_time_ticks_df: DataFrame | None = None

        self.fastest_lap_telemetry: DataFrame | None = None
        self.map_center_coordinate: tuple[float, float, float] | None = None

        self.loading_frame: DirectFrame | None = None
        self.loading_text: OnscreenText | None = None
        self.wait_bar: DirectWaitBar | None = None

        self.parsed_car_data: DataFrame | None = None

        self.accept("loadData", self.load_data)

        if not self.cache_path.exists():
            self.cache_path.mkdir(parents=True)

        fastf1.Cache.enable_cache(str(self.cache_path))

    @property
    def session(self) -> Session:
        return self.session_parser.session

    @property
    def session_start_time(self) -> Timedelta:
        return self.session_parser.session_start_time

    @property
    def session_end_time(self) -> Timedelta:
        return self.session_parser.session_end_time

    @property
    def session_results(self) -> DataFrame:
        if self._session_results is None:
            raise ValueError("Session results are not loaded yet.")

        return self._session_results

    @property
    def total_laps(self) -> int:
        return self.session_parser.total_laps

    @property
    def track_parser(self) -> TrackParser:
        if self._track_parser is None:
            self._track_parser = TrackParser(self.session)

        return self._track_parser

    @property
    def map_rotation(self) -> float:
        return self.track_parser.map_rotation

    @property
    def processed_corners(self) -> DataFrame:
        if self._processed_corners is None:
            raise ValueError("Corners are not processed yet.")

        return self._processed_corners

    @property
    def track_statuses(self) -> DataFrame:
        if self._track_statuses is None:
            raise ValueError("Track statuses not processed.")

        return self._track_statuses

    @property
    def green_flag_track_status_label(self) -> str:
        return self.track_parser.green_flag_track_status["Label"]

    @property
    def green_flag_track_status_color(self) -> LVecBase4f:
        return self.track_parser.green_flag_track_status["Color"]

    @property
    def green_flag_track_status_text_color(self) -> LVecBase4f:
        return self.track_parser.green_flag_track_status["TextColor"]

    @property
    def weather_parser(self) -> WeatherParser:
        if self._weather_parser is None:
            self._weather_parser = WeatherParser(self.session)

        return self._weather_parser

    @property
    def laps_parser(self) -> LapsParser:
        if self._laps_parser is None:
            self._laps_parser = LapsParser(self.session, self.total_laps)

        return self._laps_parser

    @property
    def pos_parser(self) -> PositionParser:
        if self._pos_parser is None:
            self._pos_parser = PositionParser(self.session)

        return self._pos_parser

    @property
    def telemetry_parser(self) -> TelemetryParser:
        if self._telemetry_parser is None:
            self._telemetry_parser = TelemetryParser(self.session)

        return self._telemetry_parser

    def get_current_lap_number(self, session_time_tick: int) -> int:
        df = self.data

        return int(math.ceil(df[df["SessionTimeTick"] == session_time_tick]["LapsCompletion"].max()))

    @property
    def lowest_z_coordinate(self) -> float:
        return self.pos_parser.lowest_z_coordinate

    @property
    def session_ticks(self) -> int:
        df = self.data.copy()

        df = df[["DriverNumber", "SessionTimeTick"]]
        df = df.groupby("DriverNumber")["SessionTimeTick"].count()

        return df.min()

    @property
    def session_time_ticks_df(self) -> DataFrame:
        if self._session_time_ticks_df is None:
            df = self.data.copy()
            df = (
                df[["SessionTimeTick", "SessionTime"]]
                .drop_duplicates(
                    keep="first",
                )
                .copy()
            )

            self._session_time_ticks_df = df

        return self._session_time_ticks_df

    def process_track_statuses(self, width: int) -> None:
        self._track_statuses = self.track_parser.parse(
            width,
            self.session_ticks,
            self.session_time_ticks_df,
            self.session_start_time,
            self.session_end_time,
        )

    def get_current_track_status(self, session_time_tick: int) -> Series | None:
        ts_df = self.track_statuses

        ts_df = ts_df[ts_df["SessionTimeTick"] <= session_time_tick]
        ts_df = ts_df[ts_df["SessionTimeTickEnd"] >= session_time_tick]

        if ts_df.empty:
            return None

        return ts_df.iloc[0]

    def get_current_weather_data(self, session_time_tick: int) -> Series | None:
        return self.weather_parser.get_current_weather_data(session_time_tick)

    def process_fastest_lap(self) -> Self:
        pos_data = self.laps_parser.fastest_lap.get_pos_data()
        resized_pos_data_df = resize_pos_data(self.map_rotation, pos_data)

        self.map_center_coordinate = find_center(resized_pos_data_df)

        self.fastest_lap_telemetry = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        self.update_loading(1)

        return self

    def parse_pos_data(self) -> Self:
        self.data = self.pos_parser.parse(
            self.session_start_time,
            self.map_rotation,
            self.map_center_coordinate,
        )

        self.update_loading(10)

        return self

    def parse_laps(self) -> Self:
        self.laps_parser.parse()

        self.update_loading(15)

        return self

    def merge_pos_and_laps(self) -> Self:
        df = self.data.copy()
        ts_df = df[["SessionTimeTick", "SessionTimeMilliseconds"]].drop_duplicates(keep="first").copy()
        laps_df = self.laps_parser.processed_laps.copy()

        for record in laps_df.itertuples():
            laps_df.loc[
                (laps_df["LapNumber"] == record.LapNumber) & (laps_df["DriverNumber"] == record.DriverNumber),
                "SessionTimeTick",
            ] = ts_df.loc[
                ts_df["SessionTimeMilliseconds"] <= record.LapStartTimeMilliseconds,
                "SessionTimeTick",
            ].max()

        laps_df.loc[laps_df["LapNumber"] == 1.0, "SessionTimeTick"] = 1
        laps_df = laps_df.dropna(subset=["SessionTimeTick"])
        laps_df["SessionTimeTick"] = laps_df["SessionTimeTick"].astype("int64")

        lap_n_tick_df = laps_df[["DriverNumber", "LapNumber", "SessionTimeTick"]]

        # Merge once to get he LapNumber and fill it for all SessionTimeTicks
        combined_df = df.merge(lap_n_tick_df, on=["DriverNumber", "SessionTimeTick"], how="left")
        combined_df["LapNumber"] = combined_df.groupby("DriverNumber")["LapNumber"].ffill()

        # Merge second time with full laps_df to get full data per SessionTimeTick
        combined_df = combined_df.merge(laps_df, on=["DriverNumber", "LapNumber"], how="left")
        combined_df = combined_df.rename(
            columns={
                "Time_x": "Time",
                "Time_y": "TimeLap",
                "SessionTimeTick_x": "SessionTimeTick",
            },
        )
        combined_df = combined_df.drop(columns=["SessionTimeTick_y"])

        self.data = combined_df

        # TODO figure out what to do with drivers that have no lap data at all. Should probably zero out everything
        #      relevant for them and DNS them

        self.update_loading(5)

        return self

    @staticmethod
    def compute_elapsed_time(df: DataFrame, start_column: str, column_name: str) -> None:
        df[column_name] = df["SessionTime"] - df[start_column]
        time_in_milliseconds = df.loc[df[column_name].notna(), column_name].dt.total_seconds() * 1e3
        df.loc[df[column_name].notna(), f"{column_name}Milliseconds"] = time_in_milliseconds.astype("int64")

    def compute_lap_completion(self) -> Self:
        df = self.data.copy()

        self.compute_elapsed_time(df, "LapStartTime", "S1ElapsedLapTime")
        self.compute_elapsed_time(df, "Sector1SessionTime", "S2ElapsedLapTime")
        self.compute_elapsed_time(df, "Sector2SessionTime", "S3ElapsedLapTime")
        self.compute_elapsed_time(df, "LapStartTime", "ElapsedLapTime")

        df["LapStartTimeMilliseconds"] = df.groupby("DriverNumber")["LapStartTimeMilliseconds"].ffill()
        df["LapEndTimeMilliseconds"] = df.groupby("DriverNumber")["LapEndTimeMilliseconds"].ffill()

        df.loc[
            (df["LapNumber"] == self.total_laps) & (df["SessionTimeMilliseconds"] > df["LapEndTimeMilliseconds"]),
            "LapNumber",
        ] = self.total_laps + 1

        df["ElapsedTimeSinceStartOfLapMilliseconds"] = df["SessionTimeMilliseconds"] - df["LapStartTimeMilliseconds"]
        df["LapPercentageCompletion"] = df["ElapsedTimeSinceStartOfLapMilliseconds"] / df["LapTimeMilliseconds"]
        df["LapPercentageCompletion"] = df["LapPercentageCompletion"].replace([np.inf, -np.inf, np.nan], 0)
        df.loc[df["LapNumber"] > self.total_laps, "LapPercentageCompletion"] = 0
        df["LapsCompletion"] = (df["LapNumber"] - 1) + df["LapPercentageCompletion"]

        self.data = df

        self.update_loading(5)

        return self

    def compute_is_dnf(self) -> Self:
        df = self.data.copy()

        df.loc[df["Position"].notna(), "IsDNF"] = False
        df.loc[df["Position"].isna(), "IsDNF"] = True

        self.data = df

        self.update_loading(1)

        return self

    def compute_is_finished(self) -> Self:
        df = self.data.copy()
        df.loc[df["LapsCompletion"] == self.total_laps, "IsFinished"] = True
        df.loc[df["IsFinished"].isna(), "IsFinished"] = False
        df.loc[df["IsFinished"], "IsDNF"] = False

        self.data = df

        self.update_loading(1)

        return self

    def compute_position_index(self) -> Self:
        df = self.data.copy()

        df["PositionIndex"] = (
            df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])
            .groupby("SessionTimeTick")
            .cumcount()
            .add(1)
            - 1
        )
        df.loc[df["SessionTimeMilliseconds"] >= self.laps_parser.end_of_race_milliseconds, "PositionIndex"] = pd.NA
        df["PositionIndex"] = df.groupby("DriverNumber")["PositionIndex"].ffill().astype("int64")

        self.data = df

        self.update_loading(2)

        return self

    def compute_fastest_lap(self) -> Self:
        df = self.data.copy()

        df["FastestLapTimeMilliseconds"] = df.sort_values(
            by=["SessionTimeTick", "LapsCompletion"],
            ascending=[True, False],
        )["FastestLapTimeMillisecondsSoFar"].cummin()
        df.loc[
            df["FastestLapTimeMillisecondsSoFar"] == df["FastestLapTimeMilliseconds"],
            "HasFastestLap",
        ] = True
        df.loc[df["HasFastestLap"].isna(), "HasFastestLap"] = False
        df["HasFastestLap"] = df.groupby("DriverNumber")["HasFastestLap"].ffill()

        self.data = df

        self.update_loading(3)

        return self

    def compute_formatted_times(self) -> Self:
        df = self.data.copy()

        df["S1ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S1ElapsedLapTimeMilliseconds"])
        df["S2ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S2ElapsedLapTimeMilliseconds"])
        df["S3ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S3ElapsedLapTimeMilliseconds"])
        df["ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["ElapsedLapTimeMilliseconds"])

        self.data = df

        return self

    def compute_diff_to_car_in_front(self) -> Self:
        df = self.data.copy()
        df.loc[
            (df["SessionTimeMilliseconds"] >= df["Sector1SessionTimeMilliseconds"]),
            "DiffToCarInFront",
        ] = df["S1DiffToCarAhead"]
        df.loc[
            (df["SessionTimeMilliseconds"] >= df["Sector2SessionTimeMilliseconds"]),
            "DiffToCarInFront",
        ] = df["S2DiffToCarAhead"]
        df.loc[
            (df["SessionTimeMilliseconds"] >= df["Sector3SessionTimeMilliseconds"]),
            "DiffToCarInFront",
        ] = df["S3DiffToCarAhead"]
        df.loc[df["PositionIndex"] == 0, "DiffToCarInFront"] = 0
        df["DiffToCarInFront"] = df.groupby("DriverNumber")["DiffToCarInFront"].ffill()
        df["DiffToCarInFront"] = round(df["DiffToCarInFront"] / 1000, 3)

        self.data = df

        self.update_loading(5)

        return self

    def compute_diff_to_leader(self) -> Self:
        df = self.data.copy()
        df["DiffToLeader"] = (
            df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])
            .groupby(["SessionTimeTick"])["DiffToCarInFront"]
            .cumsum()
        )
        df["DiffToLeader"] = round(df["DiffToLeader"], 3)

        self.data = df

        self.update_loading(5)

        return self

    def compute_in_pit(self) -> Self:
        df = self.data.copy()

        df.loc[
            (
                (df["PitInTimeMilliseconds"].notna() & (df["PitInTimeMilliseconds"] <= df["SessionTimeMilliseconds"]))
                | (
                    df["PitOutTimeMilliseconds"].notna()
                    & (df["PitOutTimeMilliseconds"] >= df["SessionTimeMilliseconds"])
                )
            ),
            "InPit",
        ] = True

        df["InPit"] = df["InPit"].astype("boolean").fillna(False)

        self.data = df

        self.update_loading(5)

        return self

    def parse_telemetry(self) -> Self:
        self.parsed_car_data = self.telemetry_parser.parse(
            self.session_start_time,
            self.session_end_time,
            self.session_time_ticks_df,
        )

        self.update_loading(15)

        return self

    def merge_pos_and_car_data(self) -> Self:
        df = self.data.copy()
        car_data = self.parsed_car_data.copy()

        combined_df = df.merge(car_data, on=["DriverNumber", "SessionTimeTick"], how="left")
        combined_df["RPM"] = combined_df.groupby("DriverNumber")["RPM"].ffill()
        combined_df["Speed"] = combined_df.groupby("DriverNumber")["Speed"].ffill()
        combined_df["SpeedMph"] = combined_df.groupby("DriverNumber")["SpeedMph"].ffill()
        combined_df["nGear"] = combined_df.groupby("DriverNumber")["nGear"].ffill()
        combined_df["Throttle"] = combined_df.groupby("DriverNumber")["Throttle"].ffill()
        combined_df["Brake"] = combined_df.groupby("DriverNumber")["Brake"].ffill()
        combined_df["DRS"] = combined_df.groupby("DriverNumber")["DRS"].ffill()
        combined_df["DRS"] = combined_df["DRS"].fillna(0)
        combined_df["DRS"] = combined_df["DRS"].astype("int64")

        self.data = combined_df

        self.update_loading(3)

        return self

    def process_weather_data(self) -> Self:
        self.weather_parser.parse(
            self.session_time_ticks_df,
            self.session_start_time,
            self.session_end_time,
        )

        self.update_loading(10)

        return self

    def process_corners(self) -> Self:
        self._processed_corners = self.track_parser.process_corners(self.map_center_coordinate)

        self.update_loading(1)

        return self

    def process_team_colors(self) -> Self:
        self._session_results = self.session_parser.process_team_colors()

        self.update_loading(1)

        return self

    def render_wait_bar(self) -> None:
        width = 400
        height = 200
        self.loading_frame = DirectFrame(
            parent=self.parent,
            frameColor=(0.20, 0.20, 0.20, 0.7),
            frameSize=(0, width, 0, -height),
            pos=Point3(
                (self.window_width / 2) - (width / 2),
                0,
                -((self.window_height / 2) - (height / 2)),
            ),
        )

        self.loading_text = OnscreenText(
            parent=self.loading_frame,
            pos=(width / 2, -(height / 2)),
            scale=width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text="Loading ...",
        )

        self.wait_bar = DirectWaitBar(
            parent=self.loading_frame,
            text="WaitBar",
            value=0,
            range=100,
            barColor=(0, 1, 0, 0.7),
            frameSize=(0, width - 20, 0, -10),
            pos=Point3(10, 0, -(height - 20)),
        )

    def update_loading(self, value: int) -> None:
        self.wait_bar["value"] += value

    def delete_loading(self) -> None:
        self.wait_bar.destroy()
        self.loading_text.destroy()
        self.loading_frame.destroy()

    def load_data(self) -> None:
        self.render_wait_bar()
        self.task_manager.add(self.extract, "extractData", taskChain="loadingData")

    def extract(self, task: Task) -> Any:
        self.session.load()
        self.update_loading(10)

        (
            self.parse_laps()
            .process_fastest_lap()
            .parse_pos_data()
            .parse_telemetry()
            .merge_pos_and_laps()
            .compute_lap_completion()
            .compute_is_dnf()
            .compute_is_finished()
            .compute_position_index()
            .compute_fastest_lap()
            .compute_formatted_times()
            .compute_diff_to_car_in_front()
            .compute_diff_to_leader()
            .compute_in_pit()
            .merge_pos_and_car_data()
            .process_weather_data()
            .process_corners()
            .process_team_colors()
        )

        self.delete_loading()
        messenger.send("sessionSelected")

        return task.done
