from direct.gui.OnscreenText import OnscreenText
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import LVecBase4f
from pandas import Series

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver


class LeaderboardProcessor:
    def __init__(
        self,
        lap_counter: OnscreenText,
        drivers: list[Driver],
        checkered_flags: list[OnscreenText],
        team_colors: list[OnscreenText],
        driver_abbreviations: list[OnscreenText],
        driver_times: list[OnscreenText],
        driver_tires: list[OnscreenText],
        has_fastest_lap: list[OnscreenText],
        data_extractor: DataExtractorService,
    ):
        self.lap_counter = lap_counter
        self.drivers = drivers
        self.checkered_flags = checkered_flags
        self.team_colors = team_colors
        self.driver_abbreviations = driver_abbreviations
        self.driver_times = driver_times
        self.driver_tires = driver_tires
        self.has_fastest_lap = has_fastest_lap
        self.data_extractor = data_extractor

    def update_driver(self, driver: Driver, current_record: Series, index: int) -> None:
        ...

    def update(self, session_time_tick: int) -> None:
        total_laps = self.data_extractor.total_laps
        current_lap_number = self.data_extractor.get_current_lap_number(session_time_tick)

        if self.lap_counter["text"] != f"LAP {current_lap_number}/{total_laps}":
            self.lap_counter["text"] = f"LAP {current_lap_number}/{total_laps}"

        for driver in self.drivers:
            current_record = driver.ticks[session_time_tick]

            index = current_record["PositionIndex"]

            default_color = LVecBase4f(1, 1, 1, 0.8)
            dnf_color = LVecBase4f(1, 1, 1, 0.5)
            current_color = self.driver_abbreviations[index].textNode.getTextColor()

            color = dnf_color if driver.is_dnf else default_color

            if driver.is_finished and self.checkered_flags[index]["text"] != "🮕":
                self.checkered_flags[index]["text"] = "🮕"
            elif not driver.is_finished and self.checkered_flags[index]["text"] != "":
                self.checkered_flags[index]["text"] = ""

            if current_color != color:
                self.driver_abbreviations[index]["fg"] = color

            if self.team_colors[index]["frameColor"] != driver.team_color_obj:
                self.team_colors[index]["frameColor"] = driver.team_color_obj

            if self.driver_abbreviations[index]["text"] != driver.abbreviation:
                self.driver_abbreviations[index]["text"] = driver.abbreviation

            if driver.has_fastest_lap:
                if self.has_fastest_lap[index]["text"] != "⏱":
                    self.has_fastest_lap[index]["text"] = "⏱"
            else:
                if self.has_fastest_lap[index]["text"] != "":
                    self.has_fastest_lap[index]["text"] = ""

            self.update_driver(driver, current_record, index)


class IntervalLeaderboardProcessor(LeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        dnf_color = LVecBase4f(1, 1, 1, 0.5)
        current_color = self.driver_times[index].textNode.getTextColor()

        if index == 0:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            if self.driver_times[index]["text"] != "Interval":
                self.driver_times[index]["text"] = "Interval"

            return

        if driver.is_dnf:
            if current_color != dnf_color:
                self.driver_times[index]["fg"] = dnf_color

            if self.driver_times[index]["text"] != "OUT":
                self.driver_times[index]["text"] = "OUT"

            return

        if driver.in_pit:
            if current_color != driver.team_color_obj:
                self.driver_times[index]["fg"] = driver.team_color_obj

            if self.driver_times[index]["text"] != "IN PIT":
                self.driver_times[index]["text"] = "IN PIT"

            return

        if current_color != default_color:
            self.driver_times[index]["fg"] = default_color

        if self.driver_times[index]["text"] != f"+{current_record['DiffToCarInFront']}":
            self.driver_times[index]["text"] = f"+{current_record['DiffToCarInFront']}"

    def update_tire_compound(self, driver: Driver, current_record: Series, index: int) -> None:
        if driver.is_dnf:
            if self.driver_tires[index]["text"] != "":
                self.driver_tires[index]["text"] = ""

            return

        tire_compound: str = current_record["Compound"]
        tire_compound__color = current_record["CompoundColor"]
        current_tire_compound_color = self.driver_tires[index].textNode.getTextColor()
        if current_tire_compound_color != tire_compound__color:
            self.driver_tires[index]["fg"] = tire_compound__color

        if self.driver_tires[index]["text"] != tire_compound:
            self.driver_tires[index]["text"] = tire_compound

    def update_driver(self, driver: Driver, current_record: Series, index: int) -> None:
        self.update_times(driver, current_record, index)
        self.update_tire_compound(driver, current_record, index)


class LeaderLeaderboardProcessor(IntervalLeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        dnf_color = LVecBase4f(1, 1, 1, 0.5)
        current_color = self.driver_times[index].textNode.getTextColor()

        if index == 0:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            if self.driver_times[index]["text"] != "Leader":
                self.driver_times[index]["text"] = "Leader"

            return

        if driver.is_dnf:
            if current_color != dnf_color:
                self.driver_times[index]["fg"] = dnf_color

            if self.driver_times[index]["text"] != "OUT":
                self.driver_times[index]["text"] = "OUT"

            return

        if driver.in_pit:
            if current_color != driver.team_color_obj:
                self.driver_times[index]["fg"] = driver.team_color_obj

            if self.driver_times[index]["text"] != "IN PIT":
                self.driver_times[index]["text"] = "IN PIT"

            return

        if current_color != default_color:
            self.driver_times[index]["fg"] = default_color

        if self.driver_times[index]["text"] != f"+{current_record['DiffToLeader']}":
            self.driver_times[index]["text"] = f"+{current_record['DiffToLeader']}"

class TiresLeaderboardProcessor(IntervalLeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        dnf_color = LVecBase4f(1, 1, 1, 0.5)
        current_color = self.driver_times[index].textNode.getTextColor()

        if driver.is_dnf:
            if current_color != dnf_color:
                self.driver_times[index]["fg"] = dnf_color

            if self.driver_times[index]["text"] != "OUT":
                self.driver_times[index]["text"] = "OUT"

            return

        tire_age = str(int(current_record["TyreLife"]))

        if current_color != default_color:
            self.driver_times[index]["fg"] = default_color

        if self.driver_times[index]["text"] != tire_age:
            self.driver_times[index]["text"] = tire_age
