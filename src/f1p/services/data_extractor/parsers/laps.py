from typing import Self

from fastf1.core import Session
from pandas import DataFrame, Series, Timedelta

from f1p.ui.enums import Colors
from f1p.utils.timedelta import td_series_to_min_n_sec


class LapsParser:
    def __init__(self, session: Session, total_laps: int):
        self.session = session
        self.total_laps = total_laps

        self._laps: DataFrame | None = None
        self._processed_laps: DataFrame | None = None

        self._slowest_non_pit_lap: Series | None = None
        self._fastest_lap: Series | None = None
        self._end_of_race_milliseconds: int | None = None

    @property
    def laps(self) -> DataFrame:
        if self._laps is None:
            self._laps = self.session.laps

        return self._laps

    @property
    def processed_laps(self) -> DataFrame:
        if self._processed_laps is None:
            raise ValueError("Laps not processed yet.")

        return self._processed_laps

    def _add_total_laps(self) -> Self:
        df = self.laps.copy()

        df["TotalLaps"] = self.total_laps

        self._processed_laps = df

        return self

    def _convert_sector_session_time_to_milliseconds(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        sector_session_time_in_milliseconds = (
            df[f"Sector{sector}SessionTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        df[f"Sector{sector}SessionTimeMilliseconds"] = sector_session_time_in_milliseconds.astype("int64")

        self._processed_laps = df

        return self

    def _convert_sector_time_to_milliseconds(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        sector_time_in_milliseconds = (
            df[f"Sector{sector}Time"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        )
        df[f"Sector{sector}TimeMilliseconds"] = sector_time_in_milliseconds.astype("int64")

        self._processed_laps = df

        return self

    def _format_sector_time_milliseconds(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        df[f"Sector{sector}TimeFormatted"] = td_series_to_min_n_sec(df[f"Sector{sector}TimeMilliseconds"])

        self._processed_laps = df

        return self

    def _compute_sector_diff_to_car_ahead(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        df[f"S{sector}DiffToCarAhead"] = (
            df.sort_values(by=[f"Sector{sector}SessionTimeMilliseconds"], ascending=[True])
            .groupby("LapNumber")[f"Sector{sector}SessionTimeMilliseconds"]
            .diff()
        )

        self._processed_laps = df

        return self

    def _compute_sector_time_best(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        sector_time_sr = df[f"Sector{sector}TimeMilliseconds"]
        df[f"Sector{sector}Best"] = sector_time_sr[sector_time_sr > 0].min()

        self._processed_laps = df

        return self

    def _compute_fastest_sector_time_milliseconds_so_far(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        df[f"FastestSector{sector}TimeMillisecondsSoFar"] = (
            df[df[f"Sector{sector}TimeMilliseconds"].gt(0) & df[f"Sector{sector}TimeMilliseconds"].notna()]
            .groupby("DriverNumber")[f"Sector{sector}TimeMilliseconds"]
            .cummin()
        )

        self._processed_laps = df

        return self

    def _compute_sector_color_code(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        df[f"Sector{sector}ColorCode"] = "Y"

        df.loc[
            (df[f"Sector{sector}TimeMilliseconds"] <= df[f"FastestSector{sector}TimeMillisecondsSoFar"])
            & (df[f"Sector{sector}TimeMilliseconds"].gt(0))
            & (df[f"Sector{sector}TimeMilliseconds"].notna()),
            f"Sector{sector}ColorCode",
        ] = "G"

        df.loc[
            (df[f"Sector{sector}TimeMilliseconds"] <= df[f"Sector{sector}Best"])
            & (df[f"Sector{sector}TimeMilliseconds"].gt(0))
            & (df[f"Sector{sector}TimeMilliseconds"].notna()),
            f"Sector{sector}ColorCode",
        ] = "P"

        self._processed_laps = df

        return self

    def _add_sector_color(self, sector: int) -> Self:
        df = self._processed_laps.copy()

        compound_mapping = {
            "Y": Colors.YELLOW,
            "G": Colors.GREEN,
            "P": Colors.PURPLE,
        }
        df[f"Sector{sector}Color"] = df[f"Sector{sector}ColorCode"].apply(lambda c: list(compound_mapping[c]))

        self._processed_laps = df

        return self

    def _compute_sector_columns(self, sector: int) -> Self:
        (
            # self._compute_sector_session_time(sector)
            self._convert_sector_session_time_to_milliseconds(sector)
            ._convert_sector_time_to_milliseconds(sector)
            ._format_sector_time_milliseconds(sector)
            ._compute_sector_diff_to_car_ahead(sector)
            ._compute_sector_time_best(sector)
            ._compute_fastest_sector_time_milliseconds_so_far(sector)
            ._compute_sector_color_code(sector)
            ._add_sector_color(sector)
        )

        return self

    def _convert_lap_start_time_to_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        lap_start_time_in_milliseconds = df["LapStartTime"].fillna(Timedelta(milliseconds=0)).dt.total_seconds() * 1e3
        df["LapStartTimeMilliseconds"] = lap_start_time_in_milliseconds.astype("int64")

        self._processed_laps = df

        return self

    def _convert_lap_time_to_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df.loc[
            df["LapTime"].notna(),
            "LapTimeMilliseconds",
        ] = df.loc[df["LapTime"].notna(), "LapTime"].dt.total_seconds() * 1e3

        self._processed_laps = df

        return self

    def _format_lap_time_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df["LapTimeFormatted"] = td_series_to_min_n_sec(df["LapTimeMilliseconds"])

        self._processed_laps = df

        return self

    def _compute_lap_end_time_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df["LapEndTimeMilliseconds"] = df["LapStartTimeMilliseconds"] + df["LapTimeMilliseconds"]

        self._processed_laps = df

        return self

    def _convert_pit_in_time_to_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        pit_in_time_in_milliseconds = df.loc[df["PitInTime"].notna(), "PitInTime"].dt.total_seconds() * 1e3
        df.loc[df["PitInTime"].notna(), "PitInTimeMilliseconds"] = pit_in_time_in_milliseconds.astype("int64")

        self._processed_laps = df

        return self

    def _convert_pit_out_time_to_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        pit_out_time_in_milliseconds = df.loc[df["PitOutTime"].notna(), "PitOutTime"].dt.total_seconds() * 1e3
        df.loc[df["PitOutTime"].notna(), "PitOutTimeMilliseconds"] = pit_out_time_in_milliseconds.astype("int64")

        self._processed_laps = df

        return self

    def _add_last_lap_time_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df["LastLapTimeMilliseconds"] = df.groupby("DriverNumber")["LapTimeMilliseconds"].shift(1)

        self._processed_laps = df

        return self

    def _add_fastest_lap_time_milliseconds_so_far(self) -> Self:
        df = self._processed_laps.copy()

        df["FastestLapTimeMillisecondsSoFar"] = df.groupby("DriverNumber")["LastLapTimeMilliseconds"].cummin()

        self._processed_laps = df

        return self

    def _fill_in_compound(self) -> Self:
        df = self._processed_laps.copy()

        df["Compound"] = df["Compound"].str[0].astype("string")
        df["Compound"] = df.groupby("DriverNumber")["Compound"].ffill()

        self._processed_laps = df

        return self

    def _add_compound_color(self) -> Self:
        df = self._processed_laps.copy()

        compound_mapping = {
            "S": Colors.SCompound,
            "M": Colors.MCompound,
            "H": Colors.HCompound,
            "I": Colors.ICompound,
            "W": Colors.WCompound,
        }
        df["CompoundColor"] = df["Compound"].apply(lambda c: list(compound_mapping[c]))

        self._processed_laps = df

        return self

    def _compute_lap_time_best_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df["LapTimeBestMilliseconds"] = df["LapTimeMilliseconds"][df["LapTimeMilliseconds"] > 0].min()

        self._processed_laps = df

        return self

    def _compute_lap_time_personal_best_milliseconds(self) -> Self:
        df = self._processed_laps.copy()

        df["LapTimePersonalBestMilliseconds"] = (
            df[df["LapTimeMilliseconds"].gt(0) & df["LapTimeMilliseconds"].notna()]
            .groupby("DriverNumber")["LapTimeMilliseconds"]
            .transform("min")
            .astype("int64")
        )

        self._processed_laps = df

        return self

    def _compute_lap_time_color_code(self) -> Self:
        df = self._processed_laps.copy()

        df["LapTimeColorCode"] = "Y"

        df.loc[
            (df["LapTimeMilliseconds"] <= df["FastestLapTimeMillisecondsSoFar"])
            & (df["LapTimeMilliseconds"].gt(0))
            & (df["LapTimeMilliseconds"].notna()),
            "LapTimeColorCode",
        ] = "G"

        df.loc[
            df["LapTimeMilliseconds"] <= df["LapTimeBestMilliseconds"],
            "LapTimeColorCode",
        ] = "P"

        self._processed_laps = df

        return self

    def _compute_lap_time_color(self) -> Self:
        df = self._processed_laps.copy()

        color_mapping = {
            "Y": Colors.YELLOW,
            "G": Colors.GREEN,
            "P": Colors.PURPLE,
        }
        df["LapTimeColor"] = df["LapTimeColorCode"].apply(lambda c: list(color_mapping[c]))

        self._processed_laps = df

        return self

    def _compute_lap_time_ratio(self) -> Self:
        df = self._processed_laps.copy()

        df["LapTimeRatio"] = df["LapTimeMilliseconds"] / self.fastest_lap["LapTimeMilliseconds"] * 100

        self._processed_laps = df

        return self

    def _compute_s2_lap_time(self) -> Self:
        df = self._processed_laps.copy()

        df["S2LapTime"] = df["Sector2SessionTime"] - df["LapStartTime"]

        self._processed_laps = df

        return self

    def parse(self) -> DataFrame:
        (
            self._add_total_laps()
            ._compute_sector_columns(1)
            ._compute_sector_columns(2)
            ._compute_sector_columns(3)
            ._convert_lap_start_time_to_milliseconds()
            ._convert_lap_time_to_milliseconds()
            ._format_lap_time_milliseconds()
            ._compute_lap_end_time_milliseconds()
            ._convert_pit_in_time_to_milliseconds()
            ._convert_pit_out_time_to_milliseconds()
            ._add_last_lap_time_milliseconds()
            ._add_fastest_lap_time_milliseconds_so_far()
            ._fill_in_compound()
            ._add_compound_color()
            ._compute_lap_time_best_milliseconds()
            ._compute_lap_time_personal_best_milliseconds()
            ._compute_lap_time_color_code()
            ._compute_lap_time_color()
            ._compute_lap_time_ratio()
            ._compute_s2_lap_time()
        )

        return self._processed_laps

    @property
    def slowest_non_pit_lap(self) -> Series:
        if self._slowest_non_pit_lap is None:
            df = self._processed_laps.copy()

            eligible_laps = df[
                df["PitInTimeMilliseconds"].isna() & df["PitOutTimeMilliseconds"].isna() & (df["TrackStatus"] == "1")
            ]
            eligible_laps = eligible_laps.sort_values("LapTime", ascending=False)

            if eligible_laps is not None:
                self._slowest_non_pit_lap = eligible_laps.iloc[0]

        return self._slowest_non_pit_lap

    @property
    def fastest_lap(self) -> Series:
        if self._fastest_lap is None:
            df = self._processed_laps.copy()

            eligible_laps = df[df["LapTimeMilliseconds"].notna() & (df["LapTimeMilliseconds"] > 0)]
            eligible_laps = eligible_laps.sort_values("LapTimeMilliseconds", ascending=True)

            if eligible_laps is not None:
                self._fastest_lap = eligible_laps.iloc[0]

        return self._fastest_lap

    @property
    def end_of_race_milliseconds(self) -> int:
        if self._end_of_race_milliseconds is None:
            self._end_of_race_milliseconds = self._processed_laps.loc[
                self._processed_laps["LapNumber"] == self._processed_laps["TotalLaps"],
                "LapEndTimeMilliseconds",
            ].min()

        return self._end_of_race_milliseconds

    def get_driver_laps(self, driver_number: str) -> DataFrame:
        df = self._processed_laps.copy()
        df = df[df["DriverNumber"] == driver_number].copy()

        return df

    def get_driver_tire_strategy(self, driver_number: str) -> dict[int, dict[str, str | int]]:
        laps_df = self._processed_laps.copy()
        df = laps_df[laps_df["DriverNumber"] == driver_number].copy()
        df = df.sort_values(by="LapNumber", ascending=True)

        strategy_df = (
            df[["Compound", "CompoundColor", "LapNumber", "Stint", "TotalLaps"]]
            .drop_duplicates(subset=["Compound", "Stint"], keep="last")
            .reset_index(drop=True)
        )
        strategy = strategy_df.set_index("Stint").to_dict(orient="index")

        return strategy
