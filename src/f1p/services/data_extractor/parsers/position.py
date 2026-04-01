from typing import Self

import pandas as pd
from fastf1.core import Session
from pandas import DataFrame, Timedelta

from f1p.utils.geometry import center_pos_data, resize_pos_data


class PositionParser:
    def __init__(self, session: Session):
        self.session = session

        self._pos_data: dict[str, DataFrame] | None = None
        self._processed_pos_data: DataFrame | None = None

    @property
    def pos_data(self) -> dict[str, DataFrame]:
        if self._pos_data is None:
            self._pos_data = self.session.pos_data

        return self._pos_data

    @property
    def processed_pos_data(self) -> DataFrame:
        if self._processed_pos_data is None:
            raise ValueError("Position data not processed yet.")

        return self._processed_pos_data

    def _combine_position_data(self) -> Self:
        drivers_pos_data = []
        for driver_number, pos_data in self.pos_data.items():
            pos_data["DriverNumber"] = driver_number
            drivers_pos_data.append(pos_data)

        self._processed_pos_data = pd.concat(drivers_pos_data, ignore_index=True)

        return self

    def _remove_records_before_session_start_time(self, session_start_time: Timedelta) -> Self:
        df = self._processed_pos_data.copy()

        self._processed_pos_data = df[df["SessionTime"] >= session_start_time]

        return self

    def _normalize_position_data(self, map_rotation: float, map_center_coordinate: tuple[float, float, float]) -> Self:
        df = self._processed_pos_data.copy()

        resized_pos_data_df = resize_pos_data(map_rotation, df)
        self._processed_pos_data = center_pos_data(map_center_coordinate, resized_pos_data_df)

        return self

    def _add_session_time_in_milliseconds(self) -> Self:
        df = self._processed_pos_data.copy()

        df["SessionTimeMilliseconds"] = (df["SessionTime"].dt.total_seconds() * 1e3).astype("int64")

        self._processed_pos_data = df

        return self

    def _add_session_time_tick(self) -> Self:
        df = self._processed_pos_data.copy()

        df["SessionTimeTick"] = df.groupby("DriverNumber").cumcount().add(1)

        self._processed_pos_data = df

        return self

    def parse(
        self,
        session_start_time: Timedelta,
        map_rotation: float,
        map_center_coordinate: tuple[float, float, float],
    ) -> DataFrame:
        (
            self._combine_position_data()
            ._remove_records_before_session_start_time(session_start_time)
            ._normalize_position_data(map_rotation, map_center_coordinate)
            ._add_session_time_in_milliseconds()
            ._add_session_time_tick()
        )

        return self._processed_pos_data
