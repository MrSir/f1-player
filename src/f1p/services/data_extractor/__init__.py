import math
from pathlib import Path
from typing import Self

import fastf1
import pandas as pd
from direct.showbase.MessengerGlobal import messenger
from fastf1.core import Session, Lap, Laps, Telemetry
from fastf1.events import EventSchedule, Event
from fastf1.mvapi import CircuitInfo
from panda3d.core import deg2Rad, LVecBase4f
from pandas import DataFrame, Timedelta

from f1p.utils.geometry import find_center, resize_pos_data, center_pos_data


class DataExtractorService:
    year: int
    event_name: str
    session_id: str
    cache_path: Path = Path(__file__).parent.parent.parent.parent.parent / '.fastf1-cache'

    def __init__(self):
        self._event_schedule: EventSchedule | None = None
        self._event: Event | None = None
        self._session: Session | None = None
        self._session_status: DataFrame | None = None
        self._session_start_time: Timedelta | None = None
        self._session_end_time: Timedelta | None = None
        self._pos_data: dict[str, Telemetry] | None = None
        self._circuit_info: CircuitInfo | None = None
        self._total_laps: int | None = None
        self._laps: Laps | None = None
        self._fastest_lap: Lap | None = None
        self.fastest_lap_telemetry: DataFrame | None = None
        self.map_center_coordinate: tuple[float, float, float] | None = None

        self.processed_pos_data: DataFrame | None = None

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

    def process_fastest_lap(self) -> Self:
        pos_data = self.fastest_lap.get_pos_data()
        resized_pos_data_df = resize_pos_data(self.map_rotation, pos_data)

        self.map_center_coordinate = find_center(resized_pos_data_df)

        self.fastest_lap_telemetry = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        return self

    def combine_position_data(self) -> Self:
        drivers_pos_data = []
        for driver_number, pos_data in self.pos_data.items():
            pos_data["DriverNumber"] = driver_number
            drivers_pos_data.append(pos_data)

        self.processed_pos_data = pd.concat(drivers_pos_data, ignore_index=True)

        return self

    def remove_records_before_session_start_time(self) -> Self:
        self.processed_pos_data = self.processed_pos_data[
            self.processed_pos_data["SessionTime"] >= self.session_start_time]

        return self

    def normalize_position_data(self) -> Self:
        df = self.processed_pos_data.copy()

        resized_pos_data_df = resize_pos_data(self.map_rotation, df)
        self.processed_pos_data = center_pos_data(self.map_center_coordinate, resized_pos_data_df)

        return self

    def add_session_time_in_milliseconds(self) -> Self:
        session_time_in_milliseconds = self.processed_pos_data["SessionTime"].dt.total_seconds() * 1e3

        self.processed_pos_data["SessionTimeMilliseconds"] = session_time_in_milliseconds.astype("int64")

        return self

    def add_common_session_time(self) -> Self:
        df = self.processed_pos_data.copy()

        df["SessionTimeTick"] = df.groupby("DriverNumber").cumcount().add(1)

        self.processed_pos_data = df

        return self

    def process_laps(self) -> Self:
        laps = self.laps.copy()

        laps.loc[laps["Sector1SessionTime"].isna(), "Sector1SessionTime"] = (
            laps.loc[laps["Sector1SessionTime"].isna(), "LapStartTime"] + laps.loc[laps["Sector1SessionTime"].isna(), "Sector1Time"]
        )
        laps.loc[laps["Sector2SessionTime"].isna(), "Sector2SessionTime"] = (
                laps.loc[laps["Sector2SessionTime"].isna(), "Sector1SessionTime"] + laps.loc[
            laps["Sector2SessionTime"].isna(), "Sector2Time"]
        )
        laps.loc[laps["Sector3SessionTime"].isna(), "Sector3SessionTime"] = (
                laps.loc[laps["Sector3SessionTime"].isna(), "Sector2SessionTime"] + laps.loc[
            laps["Sector3SessionTime"].isna(), "Sector3Time"]
        )

        lap_start_time_in_milliseconds = laps["LapStartTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["LapStartTimeMilliseconds"] = lap_start_time_in_milliseconds.astype("int64")
        sector1_session_time_in_milliseconds = laps["Sector1SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["Sector1SessionTimeMilliseconds"] = sector1_session_time_in_milliseconds.astype("int64")
        sector2_session_time_in_milliseconds = laps["Sector2SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["Sector2SessionTimeMilliseconds"] = sector2_session_time_in_milliseconds.astype("int64")
        sector3_session_time_in_milliseconds = laps["Sector3SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        laps["Sector3SessionTimeMilliseconds"] = sector3_session_time_in_milliseconds.astype("int64")

        lap_time_in_milliseconds = laps["LapTime"].fillna(Timedelta(milliseconds=1)).dt.total_seconds() * 1e3
        laps["LapTimeMilliseconds"] = lap_time_in_milliseconds.astype("int64")
        laps["LapEndTimeMilliseconds"] = laps["LapStartTimeMilliseconds"] + laps["LapTimeMilliseconds"]

        pit_in_time_in_milliseconds = laps.loc[laps["PitInTime"].notna(), "PitInTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitInTime"].notna(), "PitInTimeMilliseconds"] = pit_in_time_in_milliseconds.astype("int64")

        pit_out_time_in_milliseconds = laps.loc[laps["PitOutTime"].notna(), "PitOutTime"].dt.total_seconds() * 1e3
        laps.loc[laps["PitOutTime"].notna(), "PitOutTimeMilliseconds"] = pit_out_time_in_milliseconds.astype("int64")

        laps["S1DiffToCarAhead"] = laps.sort_values(by=["Sector1SessionTimeMilliseconds"], ascending=[True]).groupby("LapNumber")["Sector1SessionTimeMilliseconds"].diff()
        laps["S2DiffToCarAhead"] = laps.sort_values(by=["Sector2SessionTimeMilliseconds"], ascending=[True]).groupby("LapNumber")["Sector2SessionTimeMilliseconds"].diff()
        laps["S3DiffToCarAhead"] = laps.sort_values(by=["Sector3SessionTimeMilliseconds"], ascending=[True]).groupby("LapNumber")["Sector3SessionTimeMilliseconds"].diff()

        laps["LastLapTimeMilliseconds"] = laps.groupby("DriverNumber")["LapTimeMilliseconds"].shift(1)
        laps["FastestLapTimeMillisecondsSoFar"] = laps.groupby("DriverNumber")["LastLapTimeMilliseconds"].cummin()

        self._laps = laps

        return self

    def merge_pos_and_laps(self) -> Self:
        pos_data_df = self.processed_pos_data.copy()
        laps_df = self.laps.copy()

        end_of_race = laps_df.loc[laps_df["LapNumber"] == self.total_laps, "LapEndTimeMilliseconds"].min()

        for lap in laps_df.itertuples():
            pos_data_df.loc[
                (pos_data_df["DriverNumber"] == lap.DriverNumber) &
                (pos_data_df["SessionTimeMilliseconds"] >= lap.LapStartTimeMilliseconds) &
                (pos_data_df["SessionTimeMilliseconds"] < lap.LapEndTimeMilliseconds),
                "LapNumber"
            ] = lap.LapNumber

        combined_df = (
            pos_data_df.merge(laps_df, on=["DriverNumber", "LapNumber"], how="left")
            .rename(columns={"Time_x": "Time", "Time_y": "Time_Lap"})
            # .drop(columns="Time_y")
        )

        combined_df["LapNumber"] = combined_df.groupby("DriverNumber")["LapNumber"].ffill()
        combined_df["LapStartTimeMilliseconds"] = combined_df.groupby("DriverNumber")["LapStartTimeMilliseconds"].ffill()
        combined_df["LapEndTimeMilliseconds"] = combined_df.groupby("DriverNumber")["LapEndTimeMilliseconds"].ffill()

        combined_df.loc[
            (combined_df["LapNumber"] == self.total_laps) &
            (combined_df["SessionTimeMilliseconds"] > combined_df["LapEndTimeMilliseconds"]),
            "LapNumber"
        ] = self.total_laps + 1

        combined_df["ElapsedTimeSinceStartOfLapMilliseconds"] = combined_df["SessionTimeMilliseconds"] - combined_df["LapStartTimeMilliseconds"]
        combined_df["LapPercentageCompletion"] = combined_df["ElapsedTimeSinceStartOfLapMilliseconds"] / combined_df["LapTimeMilliseconds"]
        combined_df["LapPercentageCompletion"] = combined_df["LapPercentageCompletion"].fillna(0)
        combined_df["LapsCompletion"] = (combined_df["LapNumber"] - 1) + combined_df["LapPercentageCompletion"]
        combined_df["PositionIndex"] = combined_df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False]).groupby("SessionTimeTick").cumcount().add(1) - 1

        combined_df.loc[combined_df["Position"].notna(), "IsDNF"] = False
        combined_df.loc[combined_df["Position"].isna(), "IsDNF"] = True

        combined_df.loc[combined_df["LapsCompletion"] == self.total_laps, "IsFinished"] = True
        combined_df.loc[combined_df["IsFinished"].isna(), "IsFinished"] = False
        combined_df.loc[combined_df["IsFinished"], "IsDNF"] = False

        combined_df.loc[combined_df["SessionTimeMilliseconds"] >= end_of_race, "PositionIndex"] = pd.NA
        combined_df["PositionIndex"] = combined_df.groupby("DriverNumber")["PositionIndex"].ffill().astype("int64")

        combined_df["FastestLapTimeMilliseconds"] = combined_df.sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False])["FastestLapTimeMillisecondsSoFar"].cummin()
        combined_df.loc[combined_df["FastestLapTimeMillisecondsSoFar"] == combined_df["FastestLapTimeMilliseconds"], "HasFastestLap"] = True
        combined_df.loc[combined_df["HasFastestLap"].isna(), "HasFastestLap"] = False
        combined_df["HasFastestLap"] = combined_df.groupby("DriverNumber")["HasFastestLap"].ffill()

        combined_df.loc[
            (combined_df["SessionTimeMilliseconds"] >= combined_df["Sector1SessionTimeMilliseconds"]),
            "DiffToCarInFront"
        ] = combined_df["S1DiffToCarAhead"]
        combined_df.loc[
            (combined_df["SessionTimeMilliseconds"] >= combined_df["Sector2SessionTimeMilliseconds"]),
            "DiffToCarInFront"
        ] = combined_df["S2DiffToCarAhead"]
        combined_df.loc[
            (combined_df["SessionTimeMilliseconds"] >= combined_df["Sector3SessionTimeMilliseconds"]),
            "DiffToCarInFront"
        ] = combined_df["S3DiffToCarAhead"]
        combined_df.loc[
            (combined_df["PositionIndex"] == 0),
            "DiffToCarInFront"
        ] = 0
        combined_df["DiffToCarInFront"] = combined_df.groupby("DriverNumber")["DiffToCarInFront"].ffill()
        combined_df["DiffToCarInFront"] = round(combined_df["DiffToCarInFront"] / 1000, 3)

        combined_df["DiffToLeader"] = combined_df .sort_values(by=["SessionTimeTick", "LapsCompletion"], ascending=[True, False]).groupby(["SessionTimeTick"])["DiffToCarInFront"].cumsum()
        combined_df["DiffToLeader"] = round(combined_df["DiffToLeader"], 3)

        self.processed_pos_data = combined_df

        return self

    def add_in_pit_column(self) -> Self:
        df = self.processed_pos_data.copy()

        df.loc[
            (
                (
                    df["PitInTimeMilliseconds"].notna() &
                    (df["PitInTimeMilliseconds"] <= df["SessionTimeMilliseconds"])
                ) |
                (
                    df["PitOutTimeMilliseconds"].notna() &
                    (df["PitOutTimeMilliseconds"] >= df["SessionTimeMilliseconds"])
                )
            ),
            "InPit"
        ] = True

        df["InPit"] = df["InPit"].astype("boolean").fillna(False)

        self.processed_pos_data = df

        return self

    def process_tire_compound_columns(self) -> Self:
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
            columns=["SCompoundColor", "MCompoundColor", "HCompoundColor", "ICompoundColor", "WCompoundColor"]
        )

        return self

    def extract(self):
        self.session.load()

        (
            self.process_fastest_lap()
            .combine_position_data()
            .remove_records_before_session_start_time()
            .normalize_position_data()
            .add_session_time_in_milliseconds()
            .add_common_session_time()
            .process_laps()
            .merge_pos_and_laps()
            .add_in_pit_column()
            .process_tire_compound_columns()
        )

        messenger.send("sessionSelected")
