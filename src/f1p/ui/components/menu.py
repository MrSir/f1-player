import datetime

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import Point3

from f1p.services.data_extractor import DataExtractorService
from f1p.services.data_extractor.enums import SprintQualifyingSessionIdentifiers, ConventionalSessionIdentifiers


class Menu:
    def __init__(self, pixel2d, width: int, height: int, data_extractor: DataExtractorService):
        self.pixel2d = pixel2d
        self.width = width
        self.height = height
        self.data_extractor = data_extractor

        self.frame: DirectFrame | None = None
        self.year_menu: DirectOptionMenu | None = None
        self.events_menu: DirectOptionMenu | None = None
        self.session_menu: DirectOptionMenu | None = None

    @property
    def current_year(self) -> int:
        return datetime.date.today().year

    def render_frame(self) -> None:
        self.frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0, 0, 0, 0.5),
            frameSize=(0, self.width, -self.height, 0),
            pos=Point3(0, 0, 0),
        )

    def select_year(self, year: str) -> None:
        if year != "Year":
            self.data_extractor._event_schedule = None
            self.data_extractor._event = None
            self.data_extractor._session = None
            self.data_extractor._fastest_lap = None
            self.data_extractor._circuit_info = None
            messenger.send("clearMaps")
            self.data_extractor.year = int(year)

            event_schedule = self.data_extractor.event_schedule
            event_schedule = event_schedule[event_schedule["Session5"] == "Race"]

            self.events_menu["items"] = ["Event"] + event_schedule["EventName"].tolist()

    def render_year_menu(self) -> None:
        self.year_menu = DirectOptionMenu(
            parent=self.frame,
            text="options",
            scale=self.height,
            frameSize=(0, 1.7, -1, 0),
            items=["Year"] + [str(year) for year in range(2018, self.current_year + 1)],
            initialitem=0,
            highlightColor=(0.65, 0.65, 0.65, 1),
            text_scale=0.5,
            text_pos=(0.1, -0.7),
            # item_text_scale=0.1,
        )

        self.year_menu["command"] = self.select_year

    def select_event(self, event_name: str) -> None:
        if event_name != "Event":
            self.data_extractor._event = None
            self.data_extractor._session = None
            self.data_extractor._fastest_lap = None
            self.data_extractor._circuit_info = None
            messenger.send("clearMaps")
            self.data_extractor.event_name = event_name

            event = self.data_extractor.event
            match event['EventFormat']:
                case "sprint_qualifying":
                    self.session_menu["items"] = ["Session"] + SprintQualifyingSessionIdentifiers.all_values()
                case "conventional":
                    self.session_menu["items"] = ["Session"] + ConventionalSessionIdentifiers.all_values()

    def render_events_menu(self) -> None:
        self.events_menu = DirectOptionMenu(
            parent=self.frame,
            text="options",
            scale=self.height,
            command=self.select_event,
            frameSize=(0, 12, -1, 0),
            items=["Event"],
            initialitem=0,
            highlightColor=(0.65, 0.65, 0.65, 1),
            text_scale=0.5,
            text_pos=(0.1, -0.7),
            # item_text_scale=0.1,
            pos=Point3(92, 0, 0)
        )

    def select_session(self, session_id: str) -> None:
        if session_id != "Session":
            self.data_extractor._session = None
            self.data_extractor._fastest_lap = None
            self.data_extractor._circuit_info = None
            messenger.send("clearMaps")
            self.data_extractor.session_id = session_id

            self.data_extractor.extract()

    def render_session_menu(self) -> None:
        self.session_menu = DirectOptionMenu(
            parent=self.frame,
            text="options",
            scale=self.height,
            command=self.select_session,
            frameSize=(0, 4.5, -1, 0),
            items=["Session"],
            initialitem=0,
            highlightColor=(0.65, 0.65, 0.65, 1),
            text_scale=0.5,
            text_pos=(0.1, -0.7),
            # item_text_scale=0.1,
            pos=Point3(596, 0, 0)
        )


    def render(self):
        self.render_frame()
        self.render_year_menu()
        self.render_events_menu()
        self.render_session_menu()
