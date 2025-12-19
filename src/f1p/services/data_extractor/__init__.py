from pathlib import Path

import fastf1
from fastf1.core import Session
from fastf1.events import EventSchedule, Event
from fastf1.mvapi import CircuitInfo

class DataExtractorService:
    year: int
    event_name: str
    session_id: str
    cache_path: Path = Path(__file__).parent.parent.parent.parent.parent / '.fastf1-cache'

    def __init__(self):
        self._event_schedule: EventSchedule | None = None
        self._event: Event | None = None
        self._session: Session | None = None
        self._circuit_info: CircuitInfo | None = None

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
    def circuit_info(self) -> CircuitInfo:
        if self._circuit_info is None:
            self._circuit_info = self.session.get_circuit_info()

        return self._circuit_info

    def extract(self):
        self.session.load()