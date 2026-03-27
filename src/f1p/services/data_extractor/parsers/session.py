import fastf1
from direct.showbase.DirectObject import DirectObject
from fastf1.core import Session
from fastf1.events import Event, EventSchedule
from pandas import DataFrame, Timedelta

from f1p.services.data_extractor.enums import ConventionalSessionIdentifiers, SprintQualifyingSessionIdentifiers
from f1p.utils.color import hex_to_rgb_saturation


class SessionParser(DirectObject):
    def __init__(self):
        super().__init__()

        self._year: int | None = None
        self._event_name: str | None = None
        self._session_id: str | None = None

        self._event_schedule: EventSchedule | None = None
        self._event: Event | None = None
        self._session: Session | None = None

        self._session_status: DataFrame | None = None
        self._session_start_time: Timedelta | None = None
        self._session_end_time: Timedelta | None = None

        self._session_results: DataFrame | None = None
        self._total_laps: int | None = None

    @property
    def year(self) -> int:
        if self._year is None:
            raise ValueError("Year not set")

        return self._year

    @year.setter
    def year(self, value: int) -> None:
        self._year = value

    @property
    def event_name(self) -> str:
        if self._event_name is None:
            raise ValueError("Event name not set")

        return self._event_name

    @event_name.setter
    def event_name(self, value: str | None) -> None:
        self._event_name = value

    @property
    def session_id(self) -> str:
        if self._session_id is None:
            raise ValueError("Session id not set")

        return self._session_id

    @session_id.setter
    def session_id(self, value: str | None) -> None:
        self._session_id = value

    @property
    def event_schedule(self) -> EventSchedule:
        if self._event_schedule is None:
            self._event_schedule = fastf1.get_event_schedule(self.year)

        return self._event_schedule

    @property
    def race_event_names(self) -> list[str]:
        if self._year is None:
            return ["Event"]

        event_schedule = self.event_schedule
        event_schedule = event_schedule[event_schedule["Session5"] == "Race"]

        return ["Event"] + event_schedule["EventName"].tolist()

    @property
    def event(self) -> Event:
        if self._event is None:
            self._event = fastf1.get_event(self.year, self.event_name)

        return self._event

    @property
    def session_names(self) -> list[str]:
        if self._event_name is None:
            return ["Session"]

        match self.event["EventFormat"]:
            case "sprint_qualifying":
                return ["Session"] + SprintQualifyingSessionIdentifiers.all_values()
            case "conventional":
                return ["Session"] + ConventionalSessionIdentifiers.all_values()
            case _:
                return ["Session"] + ConventionalSessionIdentifiers.all_values()

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
    def session_start_time(self) -> Timedelta:
        if self._session_start_time is None:
            self._session_start_time = self.session_status[self.session_status["Status"] == "Started"].iloc[0]["Time"]

        return self._session_start_time

    @property
    def session_end_time(self) -> Timedelta:
        if self._session_end_time is None:
            self._session_end_time = self.session_status[self.session_status["Status"] == "Finalised"].iloc[0]["Time"]

        return self._session_end_time

    @property
    def session_results(self) -> DataFrame:
        if self._session_results is None:
            self._session_results = self.session.results

        return self._session_results

    @property
    def total_laps(self) -> int:
        if self._total_laps is None:
            self._total_laps = int(self.session.total_laps)

        return self._total_laps

    def reset_from_year(self) -> None:
        self._event_name = None
        self._session_id = None
        self._event_schedule = None
        self._event = None
        self._session = None

    def reset_from_event_name(self) -> None:
        self._session_id = None
        self._event = None
        self._session = None

    def reset_from_session_id(self) -> None:
        self._session = None

    def process_team_colors(self) -> DataFrame:
        df = self.session_results.copy()

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

        return df
