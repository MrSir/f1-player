from pathlib import Path

import fastf1
from fastf1.core import Session
from fastf1.mvapi import CircuitInfo

from f1p.services.data_extractor.enums import SessionIdentifiers


class DataExtractorService:
    def __init__(self, year: int, round_number: int, session_id: SessionIdentifiers):
        self.year = year
        self.round_number = round_number
        self.session_id = session_id

        self.cache_path = Path(__file__).parent.parent.parent.parent.parent / '.fastf1-cache'

        self._session: Session | None = None
        self._circuit_info: CircuitInfo | None = None

    def enable_cache(self):
        if not self.cache_path.exists():
            self.cache_path.mkdir(parents=True)

        fastf1.Cache.enable_cache(str(self.cache_path))

    @property
    def session(self) -> Session:
        if self._session is None:
            self._session = fastf1.get_session(self.year, self.round_number, self.session_id.value)
            self._session.load()

        return self._session

    @property
    def circuit_info(self) -> CircuitInfo:
        if self._circuit_info is None:
            self._circuit_info = self.session.get_circuit_info()

        return self._circuit_info


    def extract(self):
        self.enable_cache()
        print(self.circuit_info)