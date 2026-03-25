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
from fastf1.events import Event, EventSchedule
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f, NodePath, Point3, StaticTextFont, deg2Rad
from pandas import DataFrame, Series, Timedelta

from f1p.ui.enums import Colors
from f1p.utils.color import hex_to_rgb_saturation
from f1p.utils.geometry import center_pos_data, find_center, resize_pos_data
from f1p.utils.timedelta import td_series_to_min_n_sec


class DataExtractorService(DirectObject):
    year: int
    event_name: str
    session_id: str
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

        self._event_schedule: EventSchedule | None = None
        self._event: Event | None = None
        self._session: Session | None = None
        self._session_results: DataFrame | None = None
        self._session_status: DataFrame | None = None
        self._session_start_time: Timedelta | None = None
        self._session_end_time: Timedelta | None = None
        self._pos_data: dict[str, Telemetry] | None = None
        self._car_data: dict[str, Telemetry] | None = None
        self._circuit_info: CircuitInfo | None = None
        self._processed_corners: DataFrame | None = None
        self._track_status: DataFrame | None = None
        self._weather_data: DataFrame | None = None
        self.processed_weather_data: DataFrame | None = None
        self._track_status_colors: DataFrame | None = None
        self._green_flag_track_status: DataFrame | None = None
        self._track_statuses: DataFrame | None = None
        self._total_laps: int | None = None
        self._laps: DataFrame | None = None

        self._slowest_non_pit_lap: Series | None = None
        self._fastest_lap: Series | None = None
        self.fastest_lap_telemetry: DataFrame | None = None
        self.map_center_coordinate: tuple[float, float, float] | None = None

        self.loading_frame: DirectFrame | None = None
        self.loading_text: OnscreenText | None = None
        self.wait_bar: DirectWaitBar | None = None

        self.processed_pos_data: DataFrame | None = None
        self.processed_car_data: DataFrame | None = None

        self.accept("loadData", self.load_data)

        if not self.cache_path.exists():
            self.cache_path.mkdir(parents=True)

        fastf1.Cache.enable_cache(str(self.cache_path))

    @property
    def event_schedule(self) -> EventSchedule:
        if self._event_schedule is None:
            self._event_schedule = fastf1.get_event_schedule(self.year)

        return self._event_schedule

    @property
    def event(self) -> Event:
        if self._event is None:
            self._event = fastf1.get_event(self.year, self.event_name)

        return self._event

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = fastf1.get_session(self.year, self.event_name, self.session_id)

        return self._session

    @property
    def session_results(self) -> DataFrame:
        if self._session_results is None:
            raise ValueError("Session results are not loaded yet.")

        return self._session_results

    @property
    def session_status(self) -> DataFrame:
        if self._session_status is None:
            self._session_status = self.session.session_status

        return self._session_status

    @property
    def total_laps(self) -> int:
        if self._total_laps is None:
            self._total_laps = int(self.session.total_laps)

        return self._total_laps

    @property
    def pos_data(self) -> dict[str, Telemetry]:
        if self._pos_data is None:
            self._pos_data = self.session.pos_data

        return self._pos_data

    @property
    def car_data(self) -> dict[str, Telemetry]:
        if self._car_data is None:
            self._car_data = self.session.car_data

        return self._car_data

    @property
    def laps(self) -> DataFrame:
        if self._laps is None:
            self._laps = self.session.laps

        return self._laps

    def get_current_lap_number(self, session_time_tick: int) -> int:
        df = self.processed_pos_data

        return int(math.ceil(df[df["SessionTimeTick"] == session_time_tick]["LapsCompletion"].max()))

    @property
    def slowest_non_pit_lap(self) -> Series:
        if self._slowest_non_pit_lap is None:
            df = self.laps.copy()

            eligible_laps = df[
                df["PitInTimeMilliseconds"].isna()
                & df["PitOutTimeMilliseconds"].isna()
                & (df["TrackStatus"] == "1")
            ]
            eligible_laps = eligible_laps.sort_values("LapTime", ascending=False)

            if eligible_laps is not None:
                self._slowest_non_pit_lap = eligible_laps.iloc[0]

        return self._slowest_non_pit_lap

    @property
    def fastest_lap(self) -> Series:
        if self._fastest_lap is None:
            df = self.laps.copy()

            eligible_laps = df[df["LapTimeMilliseconds"].notna() & (df["LapTimeMilliseconds"] > 0)]
            eligible_laps = eligible_laps.sort_values("LapTimeMilliseconds", ascending=True)

            if eligible_laps is not None:
                self._fastest_lap = eligible_laps.iloc[0]

        return self._fastest_lap

    @property
    def lowest_z_coordinate(self) -> float:
        return self.processed_pos_data["Z"].min()

    @property
    def circuit_info(self) -> CircuitInfo:
        if self._circuit_info is None:
            self._circuit_info = self.session.get_circuit_info()

        return self._circuit_info

    @property
    def processed_corners(self) -> DataFrame:
        if self._processed_corners is None:
            raise ValueError("Corners are not processed yet.")

        return self._processed_corners

    @property
    def track_status(self) -> DataFrame:
        if self._track_status is None:
            self._track_status = self.session.track_status

        return self._track_status

    @property
    def track_status_colors(self) -> DataFrame:
        if self._track_status_colors is None:
            self._track_status_colors = DataFrame(
                data={
                    "Status": [1, 2, 4, 5, 6, 7],
                    "Label": [
                        "Green Flag",
                        "Yellow Flag",
                        "Safety Car",
                        "Red Flag",
                        "VSC Deployed",
                        "VSC Ending",
                    ],
                    "Color": [
                        LVecBase4f(0, 1, 0, 0.8),
                        LVecBase4f(1, 1, 0, 0.8),
                        LVecBase4f(1, 1, 0, 0.8),
                        LVecBase4f(1, 0, 0, 0.8),
                        LVecBase4f(1, 0.64, 0, 0.8),
                        LVecBase4f(1, 0.64, 0, 0.8),
                    ],
                    "TextColor": [
                        LVecBase4f(0, 0, 0, 0.8),
                        LVecBase4f(0, 0, 0, 0.8),
                        LVecBase4f(0, 0, 0, 0.8),
                        LVecBase4f(1, 1, 1, 0.8),
                        LVecBase4f(0, 0, 0, 0.8),
                        LVecBase4f(0, 0, 0, 0.8),
                    ],
                },
            )

        return self._track_status_colors

    @property
    def green_flag_track_status(self) -> DataFrame:
        if self._green_flag_track_status is None:
            ts_colors_df = self.track_status_colors
            self._green_flag_track_status = ts_colors_df[ts_colors_df["Status"] == 1]

        return self._green_flag_track_status

    @property
    def green_flag_track_status_label(self) -> str:
        return self.green_flag_track_status["Label"].iloc[0]

    @property
    def green_flag_track_status_color(self) -> LVecBase4f:
        return self.green_flag_track_status["Color"].iloc[0]

    @property
    def green_flag_track_status_text_color(self) -> LVecBase4f:
        return self.green_flag_track_status["TextColor"].iloc[0]

    @property
    def weather_data(self) -> DataFrame:
        if self._weather_data is None:
            self._weather_data = self.session.weather_data

        return self._weather_data

    @property
    def map_rotation(self) -> float:
        return deg2Rad(self.circuit_info.rotation)

    @property
    def session_start_time(self) -> Timedelta:
        if self._session_start_time is None:
            self._session_start_time = self.session_status[self.session_status["Status"] == "Started"].iloc[0]["Time"]

        return self._session_start_time

    @property
    def session_start_time_milliseconds(self) -> int:
        return int(self.session_start_time.total_seconds() * 1e3)

    @property
    def session_end_time(self) -> Timedelta:
        if self._session_end_time is None:
            self._session_end_time = self.session_status[self.session_status["Status"] == "Finalised"].iloc[0]["Time"]

        return self._session_end_time

    @property
    def session_end_time_milliseconds(self) -> int:
        return int(self.session_end_time.total_seconds() * 1e3)

    @property
    def session_ticks(self) -> int:
        df = self.processed_pos_data.copy()

        df = df[["DriverNumber", "SessionTimeTick"]]
        df = df.groupby("DriverNumber")["SessionTimeTick"].count()

        return df.min()

    def process_track_statuses(self, width: int) -> None:
        df = self.processed_pos_data.copy()
        df = df[["SessionTimeTick", "SessionTime"]].drop_duplicates(keep="first").copy()

        pixel_per_tick = width / self.session_ticks

        df.loc[:, "Pixel"] = (df.loc[:, "SessionTimeTick"] * pixel_per_tick) - pixel_per_tick

        ts_df = self.track_status.copy()
        ts_df = ts_df[ts_df["Time"] >= self.session_start_time]
        ts_df = ts_df[ts_df["Time"] <= self.session_end_time]

        ts_df["EndTime"] = ts_df["Time"].shift(-1).fillna(self.session_end_time)

        for record in ts_df.itertuples():
            ts_df.loc[ts_df["Time"] == record.Time, "SessionTimeTick"] = df.loc[
                df["SessionTime"] <= record.Time,
                "SessionTimeTick",
            ].max()
            ts_df.loc[ts_df["Time"] == record.Time, "SessionTimeTickEnd"] = df.loc[
                df["SessionTime"] <= record.EndTime,
                "SessionTimeTick",
            ].max()

        ts_df["SessionTimeTick"] = ts_df["SessionTimeTick"].astype("int64")
        ts_df["SessionTimeTickEnd"] = ts_df["SessionTimeTickEnd"].astype("int64")

        ts_df = ts_df.merge(df, on="SessionTimeTick", how="left")
        ts_df = ts_df.rename(columns={"Pixel": "PixelStart"}).drop(columns="SessionTime")
        ts_df = ts_df.merge(df, left_on="SessionTimeTickEnd", right_on="SessionTimeTick", how="left").rename(
            columns={"SessionTimeTick_x": "SessionTimeTick"},
        )
        ts_df = ts_df.rename(columns={"Pixel": "PixelEnd"}).drop(columns=["SessionTime", "SessionTimeTick_y"])
        ts_df = ts_df.drop(columns=["Time", "EndTime"]).reset_index(drop=True)

        ts_df["Width"] = ts_df["PixelEnd"] - ts_df["PixelStart"]
        ts_df["Status"] = ts_df["Status"].astype("int64")

        self._track_statuses = ts_df.merge(self.track_status_colors, on="Status", how="left")

    @property
    def track_statuses(self) -> DataFrame:
        if self._track_statuses is None:
            raise ValueError("Track statuses not processed.")

        return self._track_statuses

    def get_current_track_status(self, session_time_tick: int) -> Series | None:
        ts_df = self.track_statuses

        ts_df = ts_df[ts_df["SessionTimeTick"] <= session_time_tick]
        ts_df = ts_df[ts_df["SessionTimeTickEnd"] >= session_time_tick]

        if ts_df.empty:
            return None

        return ts_df.iloc[0]

    def get_current_weather_data(self, session_time_tick: int) -> Series | None:
        weather_df = self.processed_weather_data

        weather_df = weather_df[weather_df["SessionTimeTick"] <= session_time_tick]
        weather_df = weather_df.sort_values(by="SessionTimeTick", ascending=False)

        if weather_df.empty:
            return None

        return weather_df.iloc[0]

    def process_fastest_lap(self) -> Self:
        pos_data = self.fastest_lap.get_pos_data()
        resized_pos_data_df = resize_pos_data(self.map_rotation, pos_data)

        self.map_center_coordinate = find_center(resized_pos_data_df)

        self.fastest_lap_telemetry = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        self.update_loading(1)

        return self

    def combine_position_data(self) -> Self:
        drivers_pos_data = []
        for driver_number, pos_data in self.pos_data.items():
            pos_data["DriverNumber"] = driver_number
            drivers_pos_data.append(pos_data)

        self.processed_pos_data = pd.concat(drivers_pos_data, ignore_index=True)

        self.update_loading(2)

        return self

    def remove_records_before_session_start_time(self) -> Self:
        self.processed_pos_data = self.processed_pos_data[
            self.processed_pos_data["SessionTime"] >= self.session_start_time
        ]

        self.update_loading(1)

        return self

    def normalize_position_data(self) -> Self:
        df = self.processed_pos_data.copy()

        resized_pos_data_df = resize_pos_data(self.map_rotation, df)
        self.processed_pos_data = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        self.update_loading(5)

        return self

    def add_session_time_in_milliseconds(self) -> Self:
        df = self.processed_pos_data.copy()

        df["SessionTimeMilliseconds"] = (df["SessionTime"].dt.total_seconds() * 1e3).astype("int64")

        self.processed_pos_data = df

        self.update_loading(1)

        return self

    def add_session_time_tick(self) -> Self:
        df = self.processed_pos_data.copy()

        df["SessionTimeTick"] = df.groupby("DriverNumber").cumcount().add(1)

        self.processed_pos_data = df

        self.update_loading(1)

        return self

    def compute_sector_columns(self, sector: int) -> None:
        laps = self.laps.copy()

        laps.loc[laps[f"Sector{sector}SessionTime"].isna(), f"Sector{sector}SessionTime"] = (
            laps.loc[laps[f"Sector{sector}SessionTime"].isna(), "LapStartTime"]
            + laps.loc[laps[f"Sector{sector}SessionTime"].isna(), f"Sector{sector}Time"]
        )

        sector_session_time_in_milliseconds = (
            laps[f"Sector{sector}SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        laps[f"Sector{sector}SessionTimeMilliseconds"] = sector_session_time_in_milliseconds.astype("int64")

        sector_time_in_milliseconds = (
            laps[f"Sector{sector}Time"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        laps[f"Sector{sector}TimeMilliseconds"] = sector_time_in_milliseconds.astype("int64")

        laps[f"Sector{sector}TimeFormatted"] = td_series_to_min_n_sec(laps[f"Sector{sector}TimeMilliseconds"])

        laps[f"S{sector}DiffToCarAhead"] = (
            laps.sort_values(by=[f"Sector{sector}SessionTimeMilliseconds"], ascending=[True])
            .groupby("LapNumber")[f"Sector{sector}SessionTimeMilliseconds"]
            .diff()
        )
        sector_time_sr = laps[f"Sector{sector}TimeMilliseconds"]
        laps[f"Sector{sector}Best"] = sector_time_sr[sector_time_sr > 0].min()

        laps[f"FastestSector{sector}TimeMillisecondsSoFar"] = (
            laps[laps[f"Sector{sector}TimeMilliseconds"].gt(0) & laps[f"Sector{sector}TimeMilliseconds"].notna()]
            .groupby("DriverNumber")[f"Sector{sector}TimeMilliseconds"]
            .cummin()
        )

        laps[f"Sector{sector}ColorCode"] = "Y"
        laps.loc[
            (laps[f"Sector{sector}TimeMilliseconds"] <= laps[f"FastestSector{sector}TimeMillisecondsSoFar"])
            & (laps[f"Sector{sector}TimeMilliseconds"].gt(0))
            & (laps[f"Sector{sector}TimeMilliseconds"].notna()),
            f"Sector{sector}ColorCode",
        ] = "G"
        laps.loc[
            (laps[f"Sector{sector}TimeMilliseconds"] <= laps[f"Sector{sector}Best"])
            & (laps[f"Sector{sector}TimeMilliseconds"].gt(0))
            & (laps[f"Sector{sector}TimeMilliseconds"].notna()),
            f"Sector{sector}ColorCode",
        ] = "P"
        compound_mapping = {
            "Y": Colors.YELLOW,
            "G": Colors.GREEN,
            "P": Colors.PURPLE,
        }
        laps[f"Sector{sector}Color"] = laps[f"Sector{sector}ColorCode"].apply(lambda c: list(compound_mapping[c]))

        self._laps = laps

    def process_laps(self) -> Self:
        self.compute_sector_columns(1)
        self.compute_sector_columns(2)
        self.compute_sector_columns(3)

        laps = self.laps.copy()

        laps["TotalLaps"] = self.total_laps

        lap_start_time_in_milliseconds = laps["LapStartTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["LapStartTimeMilliseconds"] = lap_start_time_in_milliseconds.astype("int64")
        laps.loc[
            laps["LapTime"].notna(),
            "LapTimeMilliseconds",
        ] = laps.loc[laps["LapTime"].notna(), "LapTime"].dt.total_seconds() * 1e3

        laps["LapTimeFormatted"] = td_series_to_min_n_sec(laps["LapTimeMilliseconds"])

        laps["LapEndTimeMilliseconds"] = laps["LapStartTimeMilliseconds"] + laps["LapTimeMilliseconds"]

        pit_in_time_in_milliseconds = laps.loc[laps["PitInTime"].notna(), "PitInTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitInTime"].notna(), "PitInTimeMilliseconds"] = pit_in_time_in_milliseconds.astype("int64")

        pit_out_time_in_milliseconds = laps.loc[laps["PitOutTime"].notna(), "PitOutTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitOutTime"].notna(), "PitOutTimeMilliseconds"] = pit_out_time_in_milliseconds.astype("int64")

        laps["LastLapTimeMilliseconds"] = laps.groupby("DriverNumber")["LapTimeMilliseconds"].shift(1)
        laps["FastestLapTimeMillisecondsSoFar"] = laps.groupby("DriverNumber")["LastLapTimeMilliseconds"].cummin()

        laps["Compound"] = laps["Compound"].str[0].astype("string")
        laps["Compound"] = laps.groupby("DriverNumber")["Compound"].ffill()

        compound_mapping = {
            "S": Colors.SCompound,
            "M": Colors.MCompound,
            "H": Colors.HCompound,
            "I": Colors.ICompound,
            "W": Colors.WCompound,
        }
        laps["CompoundColor"] = laps["Compound"].apply(lambda c: list(compound_mapping[c]))

        laps["LapTimeBestMilliseconds"] = laps["LapTimeMilliseconds"][laps["LapTimeMilliseconds"] > 0].min()
        laps["LapTimePersonalBestMilliseconds"] = (
            laps[laps["LapTimeMilliseconds"].gt(0) & laps["LapTimeMilliseconds"].notna()]
            .groupby("DriverNumber")["LapTimeMilliseconds"]
            .transform("min")
            .astype("int64")
        )
        laps["LapTimeColorCode"] = "Y"
        laps.loc[
            (laps["LapTimeMilliseconds"] <= laps["FastestLapTimeMillisecondsSoFar"])
            & (laps["LapTimeMilliseconds"].gt(0))
            & (laps["LapTimeMilliseconds"].notna()),
            "LapTimeColorCode",
        ] = "G"
        laps.loc[
            laps["LapTimeMilliseconds"] <= laps["LapTimeBestMilliseconds"],
            "LapTimeColorCode",
        ] = "P"
        color_mapping = {
            "Y": Colors.YELLOW,
            "G": Colors.GREEN,
            "P": Colors.PURPLE,
        }
        laps["LapTimeColor"] = laps["LapTimeColorCode"].apply(lambda c: list(color_mapping[c]))

        self._laps = laps

        laps["LapTimeRatio"] = laps["LapTimeMilliseconds"] / self.fastest_lap["LapTimeMilliseconds"] * 100

        self._laps = laps

        # TODO figure out what to do with cases where a driver only has a X number of laps where X < Total # Laps

        self.update_loading(15)

        return self

    def merge_pos_and_laps(self) -> Self:
        df = self.processed_pos_data.copy()
        ts_df = df[["SessionTimeTick", "SessionTimeMilliseconds"]].drop_duplicates(keep="first").copy()
        laps_df = self.laps.copy()

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

        self.processed_pos_data = combined_df

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
        df = self.processed_pos_data.copy()

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

        self.processed_pos_data = df

        self.update_loading(5)

        return self

    def compute_is_dnf(self) -> Self:
        df = self.processed_pos_data.copy()

        df.loc[df["Position"].notna(), "IsDNF"] = False
        df.loc[df["Position"].isna(), "IsDNF"] = True

        self.processed_pos_data = df

        self.update_loading(1)

        return self

    def compute_is_finished(self) -> Self:
        df = self.processed_pos_data.copy()
        df.loc[df["LapsCompletion"] == self.total_laps, "IsFinished"] = True
        df.loc[df["IsFinished"].isna(), "IsFinished"] = False
        df.loc[df["IsFinished"], "IsDNF"] = False

        self.processed_pos_data = df

        self.update_loading(1)

        return self

    def compute_position_index(self) -> Self:
        df = self.processed_pos_data.copy()
        laps_df = self.laps.copy()
        end_of_race = laps_df.loc[laps_df["LapNumber"] == self.total_laps, "LapEndTimeMilliseconds"].min()

        df["PositionIndex"] = (
            df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])
            .groupby("SessionTimeTick")
            .cumcount()
            .add(1)
            - 1
        )
        df.loc[df["SessionTimeMilliseconds"] >= end_of_race, "PositionIndex"] = pd.NA
        df["PositionIndex"] = df.groupby("DriverNumber")["PositionIndex"].ffill().astype("int64")

        self.processed_pos_data = df

        self.update_loading(2)

        return self

    def compute_fastest_lap(self) -> Self:
        df = self.processed_pos_data.copy()

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

        self.processed_pos_data = df

        self.update_loading(3)

        return self

    def compute_formatted_times(self) -> Self:
        df = self.processed_pos_data.copy()

        df["S1ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S1ElapsedLapTimeMilliseconds"])
        df["S2ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S2ElapsedLapTimeMilliseconds"])
        df["S3ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["S3ElapsedLapTimeMilliseconds"])
        df["ElapsedLapTimeFormatted"] = td_series_to_min_n_sec(df["ElapsedLapTimeMilliseconds"])

        self.processed_pos_data = df

        return self

    def compute_diff_to_car_in_front(self) -> Self:
        df = self.processed_pos_data.copy()
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

        self.processed_pos_data = df

        self.update_loading(5)

        return self

    def compute_diff_to_leader(self) -> Self:
        df = self.processed_pos_data.copy()
        df["DiffToLeader"] = (
            df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])
            .groupby(["SessionTimeTick"])["DiffToCarInFront"]
            .cumsum()
        )
        df["DiffToLeader"] = round(df["DiffToLeader"], 3)

        self.processed_pos_data = df

        self.update_loading(5)

        return self

    def compute_in_pit(self) -> Self:
        df = self.processed_pos_data.copy()

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

        self.processed_pos_data = df

        self.update_loading(5)

        return self

    def combine_car_data(self) -> Self:
        drivers_car_data = []
        for driver_number, car_data in self.car_data.items():
            car_data["DriverNumber"] = driver_number
            drivers_car_data.append(car_data)

        self.processed_car_data = pd.concat(drivers_car_data, ignore_index=True)

        self.update_loading(1)

        return self

    def process_car_data(self) -> Self:
        df = self.processed_pos_data.copy()
        df = df[["SessionTimeTick", "SessionTime"]].drop_duplicates(keep="first").copy()

        car_data_df = self.processed_car_data.copy()
        car_data_df = car_data_df[car_data_df["SessionTime"] >= self.session_start_time]
        car_data_df = car_data_df[car_data_df["SessionTime"] <= self.session_end_time]

        df_sorted = (
            df.groupby("SessionTime", sort=True)["SessionTimeTick"].max().reset_index().sort_values("SessionTime")
        )
        times = df_sorted["SessionTime"].values  # sorted datetime64 array
        ticks = df_sorted["SessionTimeTick"].values
        indices = np.searchsorted(times, car_data_df["SessionTime"].values, side="right") - 1
        valid = indices >= 0
        result = np.where(valid, ticks[np.clip(indices, 0, len(ticks) - 1)], np.nan)
        car_data_df["SessionTimeTick"] = result

        # DRS
        # 0 - DRS DEACTIVATED (CLOSED)
        # 1 - DRS DISABLED
        # 2 - DRS DEACTIVATING (CLOSING)
        # 3 -
        # 8 - DRS ENABLED
        # 10 -
        # 12 -
        # 14 - DRS ACTIVATED (OPEN)

        car_data_df["nGear"] = car_data_df["nGear"].astype("int64").astype(str)
        car_data_df["nGear"] = car_data_df["nGear"].replace("0", "N")
        car_data_df["SpeedMph"] = car_data_df["Speed"] / 1.609344
        car_data_df = car_data_df.drop_duplicates(
            subset=["DriverNumber", "SessionTimeTick"],
            keep="first",
        ).reset_index()
        car_data_df = car_data_df.drop(
            columns=[
                "Time",
                "SessionTime",
                "Date",
                "Source",
            ],
        )

        self.processed_car_data = car_data_df

        self.update_loading(15)

        return self

    def merge_pos_and_car_data(self) -> Self:
        df = self.processed_pos_data.copy()
        car_data = self.processed_car_data.copy()

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

        self.processed_pos_data = combined_df

        self.update_loading(3)

        return self

    def process_weather_data(self) -> Self:
        df = self.processed_pos_data.copy()
        df = df[["SessionTimeTick", "SessionTime"]].drop_duplicates(keep="first").copy()

        weather_df = self.weather_data.copy()
        weather_df = weather_df[weather_df["Time"] >= self.session_start_time]
        weather_df = weather_df[weather_df["Time"] <= self.session_end_time]

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

        self.processed_weather_data = weather_df

        self.update_loading(10)

        return self

    def process_corners(self) -> Self:
        df = self.circuit_info.corners.copy()

        df["Label"] = df["Number"].astype(str) + df["Letter"].astype(str)
        df["AngleRad"] = df["Angle"].map(lambda d: deg2Rad(d))
        # Add Z coordinate
        df["Z"] = 0

        df = resize_pos_data(self.map_rotation, df)
        df = center_pos_data(self.map_center_coordinate, df)

        # Move Z back to 1
        df["Z"] = 1

        self._processed_corners = df

        self.update_loading(1)

        return self

    def process_team_colors(self) -> Self:
        df = self.session.results.copy()

        df["TeamColorRGBH"] = df["TeamColor"].map(lambda c: hex_to_rgb_saturation(c))
        df["TeamColorR"] = df["TeamColorRGBH"].map(lambda c: c["rgb"][0] / 255)
        df["TeamColorG"] = df["TeamColorRGBH"].map(lambda c: c["rgb"][1] / 255)
        df["TeamColorB"] = df["TeamColorRGBH"].map(lambda c: c["rgb"][2] / 255)
        df["TeamColorH"] = df["TeamColorRGBH"].map(lambda c: c["saturation_hls"])

        df["TeamColor"] = [
            (r, g, b, h) for r, g, b, h in zip(df["TeamColorR"], df["TeamColorG"], df["TeamColorB"], df["TeamColorH"])
        ]
        df = df.drop(
            columns=[
                "TeamColorRGBH",
                "TeamColorR",
                "TeamColorG",
                "TeamColorB",
                "TeamColorH",
            ],
        )

        self._session_results = df

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
            self.combine_position_data()
            .remove_records_before_session_start_time()
            .add_session_time_in_milliseconds()
            .add_session_time_tick()
            .process_laps()
            .process_fastest_lap()
            .normalize_position_data()
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
            .combine_car_data()
            .process_car_data()
            .merge_pos_and_car_data()
            .process_weather_data()
            .process_corners()
            .process_team_colors()
        )

        self.delete_loading()
        messenger.send("sessionSelected")

        return task.done

    def extract_tire_strategy(self, driver_number: str) -> dict[int, dict[str, str | int]]:
        laps_df = self.laps.copy()
        df = laps_df[laps_df["DriverNumber"] == driver_number].copy()
        df = df.sort_values(by="LapNumber", ascending=True)

        pd.set_option("display.max_rows", len(df))
        pd.set_option("display.max_columns", None)

        strategy_df = (
            df[["Compound", "CompoundColor", "LapNumber", "Stint", "TotalLaps"]]
            .drop_duplicates(subset=["Compound", "Stint"], keep="last")
            .reset_index(drop=True)
        )
        strategy = strategy_df.set_index("Stint").to_dict(orient="index")

        return strategy
