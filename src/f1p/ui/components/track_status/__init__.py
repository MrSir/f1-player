from direct.gui.DirectFrame import DirectFrame
from direct.showbase.DirectObject import DirectObject
from panda3d.core import StaticTextFont, Point3

from f1p.services.data_extractor import DataExtractorService
from f1p.ui.components.playback import PlaybackControls


class TrackStatus(DirectObject):
    def __init__(
        self,
        pixel2d,
        symbols_font: StaticTextFont,
        text_font: StaticTextFont,
        playback_controls: PlaybackControls,
        data_extractor: DataExtractorService
    ):
        super().__init__()

        self.pixel2d = pixel2d
        self.width = 215
        self.height = 3
        self.symbols_font = symbols_font
        self.text_font = text_font
        self.playback_controls = playback_controls
        self.data_extractor = data_extractor

        self.accept("sessionSelected", self.render)

        self.timeline_frame: DirectFrame | None = None

    def render_timeline_frame(self) -> None:
        self.timeline_frame = DirectFrame(
            parent=self.pixel2d,
            frameColor=(0, 1, 0, 0.8),
            frameSize=(0, self.playback_controls.width - 121, 0, -self.height),
            pos=Point3(34, 0, self.playback_controls.height - self.playback_controls.window_height)
        )

    def render(self) -> None:
        self.render_timeline_frame()

        df = self.data_extractor.processed_pos_data.copy()
        df = df[["SessionTimeTick", "SessionTime"]].drop_duplicates(keep="first")
        print(df)

        print(self.data_extractor.session_start_time)
        print(self.data_extractor.session_start_time_milliseconds)
        print(self.data_extractor.session_end_time)
        print(self.data_extractor.session_end_time_milliseconds)

        print(self.data_extractor.track_status)
