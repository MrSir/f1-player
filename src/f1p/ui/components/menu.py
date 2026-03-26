import datetime

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectGuiGlobals import DISABLED
from direct.gui.DirectOptionMenu import DirectOptionMenu
from direct.showbase.Messenger import Messenger
from direct.task.Task import TaskManager
from panda3d.core import Point3, StaticTextFont

from f1p.services.data_extractor.enums import ConventionalSessionIdentifiers, SprintQualifyingSessionIdentifiers
from f1p.services.data_extractor.parsers.session import SessionParser
from f1p.services.data_extractor.service import DataExtractorService
from f1p.ui.components.gui.drop_down import BlackDropDown


class Menu:
    def __init__(
        self,
        pixel2d,
        task_manager: TaskManager,
        messenger: Messenger,
        width: int,
        height: int,
        text_font: StaticTextFont,
        data_extractor: DataExtractorService,
        session_parser: SessionParser,
    ):
        self.pixel2d = pixel2d
        self.task_manager = task_manager
        self.messenger = messenger
        self.width = width
        self.height = height
        self.text_font = text_font
        self.data_extractor = data_extractor
        self.session_parser = session_parser

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
        self.session_parser.year = int(year) if year != "Year" else None
        self.session_parser.reset_from_year()
        self.events_menu["items"] = self.session_parser.race_event_names
        self.events_menu.setItems()

    def render_year_menu(self) -> None:
        self.year_menu = BlackDropDown(
            parent=self.frame,
            width=75,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 20,
            text="year",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Year"] + [str(year) for year in range(2018, self.current_year + 1)],
            item_scale=0.7,
            initialitem=0,
            pos=Point3(0, 0, -self.height / 2),
        )

        self.year_menu["command"] = self.select_year

    def select_event(self, event_name: str) -> None:
        self.session_parser.event_name = event_name if event_name != "Event" else None
        self.session_parser.reset_from_event_name()
        self.session_menu["items"] = self.session_parser.session_names
        self.session_menu.setItems()

    def render_events_menu(self) -> None:
        self.events_menu = BlackDropDown(
            parent=self.frame,
            command=self.select_event,
            width=529,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 20,
            text="event",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Event"],
            item_scale=0.7,
            initialitem=0,
            pos=Point3(76, 0, -self.height / 2),
        )

    def select_session(self, session_id: str) -> None:
        self.session_parser.session_id = session_id if session_id != "Session" else None
        self.session_parser.reset_from_session_id()

        if session_id != "Session":
            self.year_menu["state"] = DISABLED
            self.events_menu["state"] = DISABLED
            self.session_menu["state"] = DISABLED

            self.data_extractor.session_parser = self.session_parser

            self.messenger.send("loadData")

    def render_session_menu(self) -> None:
        self.session_menu = BlackDropDown(
            parent=self.frame,
            command=self.select_session,
            width=195,
            height=self.height,
            font=self.text_font,
            font_scale=self.height - 20,
            text="session",
            text_pos=(5, (-self.height / 2) + 13),
            items=["Session"],
            item_scale=0.7,
            initialitem=0,
            pos=Point3(606, 0, -self.height / 2),
        )

    def render(self):
        self.render_frame()
        self.render_year_menu()
        self.render_events_menu()
        self.render_session_menu()
