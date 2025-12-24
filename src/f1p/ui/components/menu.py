import datetime

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import RAISED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.showbase.MessengerGlobal import messenger
from panda3d.core import Point3, StaticTextFont, TextNode

from f1p.services.data_extractor import DataExtractorService
from f1p.services.data_extractor.enums import SprintQualifyingSessionIdentifiers, ConventionalSessionIdentifiers
from f1p.ui.components.gui.button import BlackButton
from f1p.ui.components.gui.drop_down import BlackDropDown, BlackDropDownV2


class Menu:
    def __init__(self, pixel2d, width: int, height: int, text_font: StaticTextFont, data_extractor: DataExtractorService):
        self.pixel2d = pixel2d
        self.width = width
        self.height = height
        self.text_font = text_font
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
            self.events_menu.setItems()

    def render_year_menu(self) -> None:
        self.year_menu = BlackDropDown(
            parent=self.frame,
            width=75,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 15,
            text="year",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Year"] + [str(year) for year in range(2018, self.current_year + 1)],
            initialitem=0,
            pos=Point3(0, 0, -self.height / 2)
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
        self.events_menu = BlackDropDown(
            parent=self.frame,
            command=self.select_event,
            width=529,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 15,
            text="event",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Event"],
            initialitem=0,
            pos=Point3(76, 0, -self.height / 2)
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
        self.session_menu = BlackDropDown(
            parent=self.frame,
            command=self.select_session,
            width=195,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 15,
            text="session",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Session"],
            initialitem=0,
            pos=Point3(606, 0, -self.height / 2)
        )

    def render(self):
        self.render_frame()
        self.render_year_menu()
        self.render_events_menu()
        self.render_session_menu()
