from typing import Self

from fastf1.core import Session
from fastf1.mvapi import CircuitInfo
from panda3d.core import deg2Rad
from pandas import DataFrame, Series, Timedelta

from f1p.services.data_extractor.track_statuses import (
    GreenFlagTrackStatus,
    RedFlagTrackStatus,
    SafetyCarTrackStatus,
    VSCDeployedTrackStatus,
    VSCEndingTrackStatus,
    YellowFlagTrackStatus,
)
from f1p.utils.dataframe import merge_in_session_time_ticks
from f1p.utils.geometry import center_pos_data, resize_pos_data


class TrackParser:
    def __init__(self, session: Session):
        self.session = session

        self._circuit_info: CircuitInfo | None = None
        self._corners: DataFrame | None = None
        self._track_status: DataFrame | None = None
        self._track_status_colors: DataFrame | None = None
        self._green_flag_track_status: Series | None = None

        self._augmented_session_time_ticks_df: DataFrame | None = None
        self._processed_track_statuses: DataFrame | None = None

    @property
    def circuit_info(self) -> CircuitInfo:
        if self._circuit_info is None:
            self._circuit_info = self.session.get_circuit_info()

        return self._circuit_info

    @property
    def map_rotation(self) -> float:
        return deg2Rad(self.circuit_info.rotation)

    @property
    def corners(self) -> DataFrame:
        if self._corners is None:
            self._corners = self.circuit_info.corners

        return self._corners

    @property
    def track_status(self) -> DataFrame:
        if self._track_status is None:
            self._track_status = self.session.track_status

        return self._track_status

    @property
    def track_status_colors(self) -> DataFrame:
        if self._track_status_colors is None:
            self._track_status_colors = DataFrame(
                data=[
                    GreenFlagTrackStatus(),
                    YellowFlagTrackStatus(),
                    SafetyCarTrackStatus(),
                    RedFlagTrackStatus(),
                    VSCDeployedTrackStatus(),
                    VSCEndingTrackStatus(),
                ],
            )

        return self._track_status_colors

    @property
    def green_flag_track_status(self) -> Series:
        if self._green_flag_track_status is None:
            self._green_flag_track_status = GreenFlagTrackStatus()

        return self._green_flag_track_status

    def process_corners(self, map_center_coordinate: tuple[float, float, float]) -> DataFrame:
        df = self.corners.copy()

        df["Label"] = df["Number"].astype(str) + df["Letter"].astype(str)
        df["AngleRad"] = df["Angle"].map(lambda d: deg2Rad(d))
        # Add Z coordinate
        df["Z"] = 0

        df = resize_pos_data(self.map_rotation, df)
        df = center_pos_data(map_center_coordinate, df)

        # Move Z back to 1
        df["Z"] = 1

        return df

    def _augment_session_time_ticks(self, width: int, session_ticks: int, session_time_ticks_df: DataFrame) -> Self:
        df = session_time_ticks_df.copy()

        pixel_per_tick = width / session_ticks
        pixel_sr = (df.loc[:, "SessionTimeTick"] * pixel_per_tick) - pixel_per_tick
        df.loc[:, "Pixel"] = pixel_sr

        self._augmented_session_time_ticks_df = df

        return self

    def _trim_to_session_time(
        self,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> Self:
        df = self.track_status.copy()
        df = df[df["Time"] >= session_start_time]
        df = df[df["Time"] <= session_end_time]

        df["EndTime"] = df["Time"].shift(-1).fillna(session_end_time)

        self._processed_track_statuses = df.reset_index(drop=True)

        return self

    def _add_session_time_ticks(self) -> Self:
        ts_df = merge_in_session_time_ticks(
            self._processed_track_statuses,
            self._augmented_session_time_ticks_df,
            target_df_comparison_column="Time",
        )
        ts_df = merge_in_session_time_ticks(
            ts_df,
            self._augmented_session_time_ticks_df,
            target_df_comparison_column="EndTime",
            target_df_result_column="SessionTimeTickEnd",
        )

        self._processed_track_statuses = ts_df

        return self

    def _merge_in_augmented_session_time_ticks(self) -> Self:
        df = self._processed_track_statuses.copy()

        # Pixel Start
        df = df.merge(self._augmented_session_time_ticks_df, on="SessionTimeTick", how="left")
        df = df.rename(columns={"Pixel": "PixelStart"}).drop(columns="SessionTime")

        # Pixel End
        df = df.merge(
            self._augmented_session_time_ticks_df,
            left_on="SessionTimeTickEnd",
            right_on="SessionTimeTick",
            how="left",
        ).rename(columns={"SessionTimeTick_x": "SessionTimeTick"})

        # Cleanup
        df = (
            df.rename(columns={"Pixel": "PixelEnd"})
            .drop(
                columns=["SessionTime", "SessionTimeTick_y", "Time", "EndTime"],
            )
            .reset_index(drop=True)
        )

        self._processed_track_statuses = df

        return self

    def _compute_width(self) -> Self:
        df = self._processed_track_statuses.copy()

        df["Width"] = df["PixelEnd"] - df["PixelStart"]

        self._processed_track_statuses = df

        return self

    def _convert_status_to_integer(self) -> Self:
        df = self._processed_track_statuses.copy()

        df["Status"] = df["Status"].astype("int64")

        self._processed_track_statuses = df

        return self

    def _merge_status_colors(self) -> Self:
        df = self._processed_track_statuses.copy()

        df = df.merge(self.track_status_colors, on="Status", how="left")

        self._processed_track_statuses = df

        return self

    def parse(
        self,
        width: int,
        session_ticks: int,
        session_time_ticks_df: DataFrame,
        session_start_time: Timedelta,
        session_end_time: Timedelta,
    ) -> DataFrame:
        (
            self._augment_session_time_ticks(width, session_ticks, session_time_ticks_df)
            ._trim_to_session_time(session_start_time, session_end_time)
            ._add_session_time_ticks()
            ._merge_in_augmented_session_time_ticks()
            ._compute_width()
            ._convert_status_to_integer()
            ._merge_status_colors()
        )

        return self._processed_track_statuses
