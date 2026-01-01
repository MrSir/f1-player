from direct.gui.OnscreenText import OnscreenText
from panda3d.core import LVecBase4f
from pandas import DataFrame, Series

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.driver import Driver


class LeaderboardProcessor:
    def __init__(
        self,
        lap_counter: OnscreenText,
        drivers: list[Driver],
        team_colors: list[OnscreenText],
        driver_abbreviations: list[OnscreenText],
        driver_times: list[OnscreenText],
        driver_tires: list[OnscreenText],
        data_extractor: DataExtractorService,
    ):
        self.lap_counter = lap_counter
        self.drivers = drivers
        self.team_colors = team_colors
        self.driver_abbreviations = driver_abbreviations
        self.driver_times = driver_times
        self.driver_tires = driver_tires
        self.data_extractor = data_extractor

    def update_driver(self, driver: Driver, current_record: Series, index: int) -> None:
        ...

    def update(self, session_time_tick: int) -> None:
        total_laps = self.data_extractor.session.total_laps
        current_lap_number = self.data_extractor.get_current_lap_number(session_time_tick)

        if self.lap_counter["text"] != f"LAP {current_lap_number}/{total_laps}":
            self.lap_counter["text"] = f"LAP {current_lap_number}/{total_laps}"

        for driver in self.drivers:
            current_record = driver.pos_data[driver.pos_data["SessionTimeTick"] == session_time_tick].iloc[0]

            index = current_record["Position"] - 1

            if index > len(self.drivers) - 1:
                continue

            if self.team_colors[index]["frameColor"] != driver.team_color_obj:
                self.team_colors[index]["frameColor"] = driver.team_color_obj

            if self.driver_abbreviations[index]["text"] != driver.abbreviation:
                self.driver_abbreviations[index]["text"] = driver.abbreviation

            self.update_driver(driver, current_record, index)


class IntervalLeaderboardProcessor(LeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        current_color = self.driver_times[index].textNode.getTextColor()

        if index == 0:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            if self.driver_times[index]["text"] != "Interval":
                self.driver_times[index]["text"] = "Interval"

            return

        if current_record["InPit"]:
            if current_color != driver.team_color_obj:
                self.driver_times[index]["fg"] = driver.team_color_obj

            if self.driver_times[index]["text"] != "IN PIT":
                self.driver_times[index]["text"] = "IN PIT"
        else:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            # TODO interval times
            if self.driver_times[index]["text"] != "+1.23":
                self.driver_times[index]["text"] = "+1.23"

    def update_tire_compound(self, current_record: Series, index: int) -> None:
        tire_compound: str = current_record["Compound"]
        tire_compound__color = current_record["CompoundColor"]
        current_tire_compound_color = self.driver_tires[index].textNode.getTextColor()
        if current_tire_compound_color != tire_compound__color:
            self.driver_tires[index]["fg"] = tire_compound__color

        if self.driver_tires[index]["text"] != tire_compound:
            self.driver_tires[index]["text"] = tire_compound

    def update_driver(self, driver: Driver, current_record: Series, index: int) -> None:
        self.update_times(driver, current_record, index)
        self.update_tire_compound(current_record, index)


class LeaderLeaderboardProcessor(IntervalLeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        current_color = self.driver_times[index].textNode.getTextColor()

        if index == 0:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            if self.driver_times[index]["text"] != "Leader":
                self.driver_times[index]["text"] = "Leader"

            return

        if current_record["InPit"]:
            if current_color != driver.team_color_obj:
                self.driver_times[index]["fg"] = driver.team_color_obj

            if self.driver_times[index]["text"] != "IN PIT":
                self.driver_times[index]["text"] = "IN PIT"
        else:
            if current_color != default_color:
                self.driver_times[index]["fg"] = default_color

            # TODO time to leader
            if self.driver_times[index]["text"] != "+1.23":
                self.driver_times[index]["text"] = "+1.23"


class PitsLeaderboardProcessor(LeaderboardProcessor):
    def update_driver(self, driver: Driver, current_record: Series, index: int) -> None:
        pass


class TiresLeaderboardProcessor(IntervalLeaderboardProcessor):
    def update_times(self, driver: Driver, current_record: Series, index: int) -> None:
        default_color = LVecBase4f(1, 1, 1, 0.8)
        current_color = self.driver_times[index].textNode.getTextColor()

        tire_age = str(int(current_record["TyreLife"]))

        if current_color != default_color:
            self.driver_times[index]["fg"] = default_color

        if self.driver_times[index]["text"] != tire_age:
            self.driver_times[index]["text"] = tire_age
