from typing import Self

import pandas as pd
from fastf1.core import Session
from pandas import DataFrame, Timedelta

from f1p.utils.dataframe import merge_in_session_time_ticks


class TelemetryParser:
    def __init__(self, session: Session):
        self.session = session

        self._car_data: dict[str, DataFrame] | None = None
        self._processed_car_data: DataFrame | None = None

    @property
    def car_data(self) -> dict[str, DataFrame]:
        if self._car_data is None:
            self._car_data = self.session.car_data

        return self._car_data

    @property
    def processed_car_data(self) -> DataFrame:
        if self._processed_car_data is None:
            raise ValueError("Car data not processed yet.")

        return self._processed_car_data

    def _combine_car_data(self) -> Self:
        drivers_car_data = []
        for driver_number, car_data in self.car_data.items():
            car_data["DriverNumber"] = driver_number
            drivers_car_data.append(car_data)

        self._processed_car_data = pd.concat(drivers_car_data, ignore_index=True)

        return self

    def _trim_to_session_time(
        self,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> Self:
        df = self._processed_car_data.copy()
        df = df[df["SessionTime"] >= session_start_time]
        df = df[df["SessionTime"] <= session_end_time]

        self._processed_car_data = df.reset_index(drop=True)

        return self

    def _add_session_time_ticks(self, session_time_ticks_df: DataFrame) -> Self:
        df = merge_in_session_time_ticks(self._processed_car_data, session_time_ticks_df)

        self._processed_car_data = df

        return self

    def _normalize_gear_indicator(self) -> Self:
        df = self._processed_car_data.copy()

        df["nGear"] = df["nGear"].astype("int64").astype(str).replace("0", "N")

        self._processed_car_data = df

        return self

    def _convert_speed_to_mph(self) -> Self:
        df = self._processed_car_data.copy()

        df["SpeedMph"] = df["Speed"] / 1.609344

        self._processed_car_data = df

        return self

    def _clean_up(self) -> Self:
        df = self._processed_car_data.copy()

        df = df.drop_duplicates(
            subset=["DriverNumber", "SessionTimeTick"],
            keep="first",
        ).reset_index(drop=True)

        df = df.drop(
            columns=[
                "Time",
                "SessionTime",
                "Date",
                "Source",
            ],
        )

        self._processed_car_data = df

        return self

    def parse(
        self,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
        session_time_ticks_df: DataFrame,
    ) -> DataFrame:
        (
            self._combine_car_data()
            ._trim_to_session_time(session_start_time, session_end_time)
            ._add_session_time_ticks(session_time_ticks_df)
            ._normalize_gear_indicator()
            ._convert_speed_to_mph()
            ._clean_up()
        )

        return self._processed_car_data
