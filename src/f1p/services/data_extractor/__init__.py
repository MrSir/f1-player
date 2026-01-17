import math
from pathlib import Path
from typing import Self, Any

import fastf1
import pandas as pd
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectWaitBar import DirectWaitBar
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.DirectObject import DirectObject
from direct.task.Task import TaskManager, Task
from fastf1.core import Lap, Laps, Session, Telemetry
from fastf1.events import Event, EventSchedule
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f, deg2Rad, NodePath, Point3, StaticTextFont
from pandas import DataFrame, Series, Timedelta

from f1p.utils.geometry import center_pos_data, find_center, resize_pos_data
from f1p.utils.performance import timeit


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
        self.parent = parent
        self.task_manager = task_manager
        self.window_width = window_width
        self.window_height = window_height
        self.text_font = text_font

        self._event_schedule: EventSchedule | None = None
        self._event: Event | None = None
        self._session: Session | None = None
        self._session_status: DataFrame | None = None
        self._session_start_time: Timedelta | None = None
        self._session_end_time: Timedelta | None = None
        self._pos_data: dict[str, Telemetry] | None = None
        self._circuit_info: CircuitInfo | None = None
        self._track_status: DataFrame | None = None
        self._track_status_colors: DataFrame | None = None
        self._green_flag_track_status: DataFrame | None = None
        self._track_statuses: DataFrame | None = None
        self._total_laps: int | None = None
        self._laps: Laps | None = None
        self._fastest_lap: Lap | None = None
        self.fastest_lap_telemetry: DataFrame | None = None
        self.map_center_coordinate: tuple[float, float, float] | None = None

        self.loading_frame: DirectFrame | None = None
        self.loading_text: OnscreenText | None = None
        self.progress_text: OnscreenText | None = None
        self.wait_bar: DirectWaitBar | None = None

        self.processed_pos_data: DataFrame | None = None

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
    def laps(self) -> Laps:
        if self._laps is None:
            self._laps = self.session.laps

        return self._laps

    def get_current_lap_number(self, session_time_tick: int) -> int:
        df = self.processed_pos_data
        df = df[df["SessionTimeTick"] == session_time_tick]

        return int(math.ceil(df["LapsCompletion"].max()))

    @property
    def fastest_lap(self) -> Lap:
        if self._fastest_lap is None:
            self._fastest_lap = self.laps.pick_fastest()

        return self._fastest_lap

    @property
    def circuit_info(self) -> CircuitInfo:
        if self._circuit_info is None:
            self._circuit_info = self.session.get_circuit_info()

        return self._circuit_info

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

        df.loc[:, "Pixel"] = df.loc[:, "SessionTimeTick"] * pixel_per_tick

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
        ts_df = ts_df.drop(columns=["Time", "EndTime"]).reset_index()

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

    @timeit
    def process_fastest_lap(self) -> Self:
        self.update_loading(9, "Processing Fastest Lap")
        pos_data = self.fastest_lap.get_pos_data()
        resized_pos_data_df = resize_pos_data(self.map_rotation, pos_data)

        self.map_center_coordinate = find_center(resized_pos_data_df)

        self.fastest_lap_telemetry = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        return self

    @timeit
    def combine_position_data(self) -> Self:
        self.update_loading(11, "Combining Position Data")
        drivers_pos_data = []
        for driver_number, pos_data in self.pos_data.items():
            pos_data["DriverNumber"] = driver_number
            drivers_pos_data.append(pos_data)

        self.processed_pos_data = pd.concat(drivers_pos_data, ignore_index=True)

        return self

    @timeit
    def remove_records_before_session_start_time(self) -> Self:
        self.update_loading(12, "Removing Pre Start Data")
        self.processed_pos_data = self.processed_pos_data[
            self.processed_pos_data["SessionTime"] >= self.session_start_time
            ]

        return self

    @timeit
    def normalize_position_data(self) -> Self:
        self.update_loading(13, "Normalize Position Data")
        df = self.processed_pos_data.copy()

        resized_pos_data_df = resize_pos_data(self.map_rotation, df)
        self.processed_pos_data = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        return self

    @timeit
    def add_session_time_in_milliseconds(self) -> Self:
        self.update_loading(14, "Convert Time to Milliseconds")
        session_time_in_milliseconds = self.processed_pos_data["SessionTime"].dt.total_seconds() * 1e3

        self.processed_pos_data["SessionTimeMilliseconds"] = session_time_in_milliseconds.astype("int64")

        return self

    @timeit
    def add_session_time_tick(self) -> Self:
        self.update_loading(15, "Adding Session Time Tick")
        df = self.processed_pos_data.copy()

        df["SessionTimeTick"] = df.groupby("DriverNumber").cumcount().add(1)

        self.processed_pos_data = df

        return self

    @timeit
    def process_laps(self) -> Self:
        self.update_loading(16, "Processing Lap Data")
        laps = self.laps.copy()

        laps.loc[laps["Sector1SessionTime"].isna(), "Sector1SessionTime"] = (
                laps.loc[laps["Sector1SessionTime"].isna(), "LapStartTime"]
                + laps.loc[laps["Sector1SessionTime"].isna(), "Sector1Time"]
        )
        laps.loc[laps["Sector2SessionTime"].isna(), "Sector2SessionTime"] = (
                laps.loc[laps["Sector2SessionTime"].isna(), "Sector1SessionTime"]
                + laps.loc[laps["Sector2SessionTime"].isna(), "Sector2Time"]
        )
        laps.loc[laps["Sector3SessionTime"].isna(), "Sector3SessionTime"] = (
                laps.loc[laps["Sector3SessionTime"].isna(), "Sector2SessionTime"]
                + laps.loc[laps["Sector3SessionTime"].isna(), "Sector3Time"]
        )

        lap_start_time_in_milliseconds = laps["LapStartTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["LapStartTimeMilliseconds"] = lap_start_time_in_milliseconds.astype("int64")
        sector1_session_time_in_milliseconds = (
                laps["Sector1SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        laps["Sector1SessionTimeMilliseconds"] = sector1_session_time_in_milliseconds.astype("int64")
        sector2_session_time_in_milliseconds = (
                laps["Sector2SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        laps["Sector2SessionTimeMilliseconds"] = sector2_session_time_in_milliseconds.astype("int64")
        sector3_session_time_in_milliseconds = (
                laps["Sector3SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        laps["Sector3SessionTimeMilliseconds"] = sector3_session_time_in_milliseconds.astype("int64")

        lap_time_in_milliseconds = laps["LapTime"].fillna(Timedelta(milliseconds=1)).dt.total_seconds() * 1e3
        laps["LapTimeMilliseconds"] = lap_time_in_milliseconds.astype("int64")
        laps["LapEndTimeMilliseconds"] = laps["LapStartTimeMilliseconds"] + laps["LapTimeMilliseconds"]

        pit_in_time_in_milliseconds = laps.loc[laps["PitInTime"].notna(), "PitInTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitInTime"].notna(), "PitInTimeMilliseconds"] = pit_in_time_in_milliseconds.astype("int64")

        pit_out_time_in_milliseconds = laps.loc[laps["PitOutTime"].notna(), "PitOutTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitOutTime"].notna(), "PitOutTimeMilliseconds"] = pit_out_time_in_milliseconds.astype("int64")

        laps["S1DiffToCarAhead"] = (
            laps.sort_values(by=["Sector1SessionTimeMilliseconds"], ascending=[True])
            .groupby("LapNumber")["Sector1SessionTimeMilliseconds"]
            .diff()
        )
        laps["S2DiffToCarAhead"] = (
            laps.sort_values(by=["Sector2SessionTimeMilliseconds"], ascending=[True])
            .groupby("LapNumber")["Sector2SessionTimeMilliseconds"]
            .diff()
        )
        laps["S3DiffToCarAhead"] = (
            laps.sort_values(by=["Sector3SessionTimeMilliseconds"], ascending=[True])
            .groupby("LapNumber")["Sector3SessionTimeMilliseconds"]
            .diff()
        )

        laps["LastLapTimeMilliseconds"] = laps.groupby("DriverNumber")["LapTimeMilliseconds"].shift(1)
        laps["FastestLapTimeMillisecondsSoFar"] = laps.groupby("DriverNumber")["LastLapTimeMilliseconds"].cummin()

        self._laps = laps

        return self

    @timeit
    def merge_pos_and_laps(self) -> Self:
        self.update_loading(17, "Merging Pos and Lap Data")

        df = self.processed_pos_data.copy()
        laps_df = self.laps.copy()

        # TODO this is the slow crap we need to fix
        #      find a way to put the lap number for each driver based on SessionTime
        for lap in laps_df.itertuples():
            df.loc[
                (df["DriverNumber"] == lap.DriverNumber)
                & (df["SessionTimeMilliseconds"] >= lap.LapStartTimeMilliseconds)
                & (df["SessionTimeMilliseconds"] < lap.LapEndTimeMilliseconds),
                "LapNumber",
            ] = lap.LapNumber

        combined_df = df.merge(laps_df, on=["DriverNumber", "LapNumber"], how="left").rename(
            columns={"Time_x": "Time", "Time_y": "Time_Lap"},
        )
        combined_df["LapNumber"] = combined_df.groupby("DriverNumber")["LapNumber"].ffill()

        self.processed_pos_data = combined_df

        return self

    @timeit
    def compute_lap_completion(self) -> Self:
        df = self.processed_pos_data.copy()

        df["LapStartTimeMilliseconds"] = df.groupby("DriverNumber")["LapStartTimeMilliseconds"].ffill()
        df["LapEndTimeMilliseconds"] = df.groupby("DriverNumber")["LapEndTimeMilliseconds"].ffill()

        df.loc[
            (df["LapNumber"] == self.total_laps)
            & (df["SessionTimeMilliseconds"] > df["LapEndTimeMilliseconds"]),
            "LapNumber",
        ] = self.total_laps + 1

        df["ElapsedTimeSinceStartOfLapMilliseconds"] = df["SessionTimeMilliseconds"] - df["LapStartTimeMilliseconds"]
        df["LapPercentageCompletion"] = df["ElapsedTimeSinceStartOfLapMilliseconds"] / df["LapTimeMilliseconds"]
        df["LapPercentageCompletion"] = df["LapPercentageCompletion"].fillna(0)
        df["LapsCompletion"] = (df["LapNumber"] - 1) + df["LapPercentageCompletion"]

        self.processed_pos_data = df

        return self

    @timeit
    def compute_is_dnf(self) -> Self:
        df = self.processed_pos_data.copy()

        df.loc[df["Position"].notna(), "IsDNF"] = False
        df.loc[df["Position"].isna(), "IsDNF"] = True

        self.processed_pos_data = df

        return self

    @timeit
    def compute_is_finished(self) -> Self:
        df = self.processed_pos_data.copy()
        df.loc[df["LapsCompletion"] == self.total_laps, "IsFinished"] = True
        df.loc[df["IsFinished"].isna(), "IsFinished"] = False
        df.loc[df["IsFinished"], "IsDNF"] = False

        self.processed_pos_data = df

        return self

    @timeit
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

        return self

    @timeit
    def compute_fastest_lap(self) -> Self:
        df = self.processed_pos_data.copy()

        df["FastestLapTimeMilliseconds"] = df.sort_values(
            by=["SessionTimeTick", "LapsCompletion"],
            ascending=[True, False],
        )["FastestLapTimeMillisecondsSoFar"].cummin()
        df.loc[df["FastestLapTimeMillisecondsSoFar"] == df["FastestLapTimeMilliseconds"], "HasFastestLap"] = True
        df.loc[df["HasFastestLap"].isna(), "HasFastestLap"] = False
        df["HasFastestLap"] = df.groupby("DriverNumber")["HasFastestLap"].ffill()

        self.processed_pos_data = df

        return self

    @timeit
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

        return self

    @timeit
    def compute_diff_to_leader(self) -> Self:
        df = self.processed_pos_data.copy()
        df["DiffToLeader"] = (
            df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])
            .groupby(["SessionTimeTick"])["DiffToCarInFront"]
            .cumsum()
        )
        df["DiffToLeader"] = round(df["DiffToLeader"], 3)

        self.processed_pos_data = df

        return self

    @timeit
    def compute_in_pit(self) -> Self:
        self.update_loading(98, "Computing In Pit Times")
        df = self.processed_pos_data.copy()

        df.loc[
            (
                    (df["PitInTimeMilliseconds"].notna() & (
                            df["PitInTimeMilliseconds"] <= df["SessionTimeMilliseconds"]))
                    | (
                            df["PitOutTimeMilliseconds"].notna()
                            & (df["PitOutTimeMilliseconds"] >= df["SessionTimeMilliseconds"])
                    )
            ),
            "InPit",
        ] = True

        df["InPit"] = df["InPit"].astype("boolean").fillna(False)

        self.processed_pos_data = df

        return self

    @timeit
    def compute_tire_compound(self) -> Self:
        self.update_loading(99, "Processing Tire Compounds")
        df = self.processed_pos_data.copy()

        df["Compound"] = df["Compound"].str[0].astype("string")
        df["Compound"] = df.groupby("DriverNumber")["Compound"].ffill()
        df["SCompoundColor"] = LVecBase4f(1, 0, 0, 0.8)
        df["MCompoundColor"] = LVecBase4f(1, 1, 0, 0.8)
        df["HCompoundColor"] = LVecBase4f(1, 1, 1, 0.8)
        df["ICompoundColor"] = LVecBase4f(0, 1, 0, 0.8)
        df["WCompoundColor"] = LVecBase4f(0, 0, 1, 0.8)

        df.loc[df["Compound"] == "S", "CompoundColor"] = df.loc[df["Compound"] == "S", "SCompoundColor"]
        df.loc[df["Compound"] == "M", "CompoundColor"] = df.loc[df["Compound"] == "M", "MCompoundColor"]
        df.loc[df["Compound"] == "H", "CompoundColor"] = df.loc[df["Compound"] == "H", "HCompoundColor"]
        df.loc[df["Compound"] == "I", "CompoundColor"] = df.loc[df["Compound"] == "I", "ICompoundColor"]
        df.loc[df["Compound"] == "W", "CompoundColor"] = df.loc[df["Compound"] == "W", "WCompoundColor"]

        self.processed_pos_data = df.drop(
            columns=["SCompoundColor", "MCompoundColor", "HCompoundColor", "ICompoundColor", "WCompoundColor"],
        )

        return self

    def render_wait_bar(self) -> None:
        width = 400
        height = 200
        self.loading_frame = DirectFrame(
            parent=self.parent,
            frameColor=(0.20, 0.20, 0.20, 0.7),
            frameSize=(0, width, 0, -height),
            pos=Point3((self.window_width / 2) - (width / 2), 0, -((self.window_height / 2) - (height / 2))),
        )

        self.loading_text = OnscreenText(
            parent=self.loading_frame,
            pos=(width / 2, -(height / 2) + 20),
            scale=width / 10,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text=f"Loading",
        )

        self.progress_text = OnscreenText(
            parent=self.loading_frame,
            pos=(width / 2, -(height / 2) - 30),
            scale=width / 15,
            fg=(1, 1, 1, 0.8),
            font=self.text_font,
            text=f"",
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

    def update_loading(self, value: int, text: str) -> None:
        self.progress_text["text"] = text
        self.wait_bar["value"] = value

    def delete_loading(self) -> None:
        self.progress_text.destroy()
        self.wait_bar.destroy()
        self.loading_text.destroy()
        self.loading_frame.destroy()

    def load_data(self) -> None:
        self.render_wait_bar()
        self.task_manager.add(self.extract, "extractData", taskChain="loadingData")

    @timeit
    def extract(self, task: Task) -> Any:
        self.update_loading(0, "Session Data")
        self.session.load()

        (
            self.process_fastest_lap()
            .combine_position_data()
            .remove_records_before_session_start_time()
            .normalize_position_data()
            .add_session_time_in_milliseconds()
            .add_session_time_tick()
            .process_laps()
            .merge_pos_and_laps()
            .compute_lap_completion()
            .compute_is_dnf()
            .compute_is_finished()
            .compute_position_index()
            .compute_fastest_lap()
            .compute_diff_to_car_in_front()
            .compute_diff_to_leader()
            .compute_in_pit()
            .compute_tire_compound()
        )

        self.update_loading(100, "Finished")
        self.delete_loading()
        # messenger.send("sessionSelected")
        return task.done
