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
        self.width = playback_controls.width - 121
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
            frameSize=(0, self.width, 0, -self.height),
            pos=Point3(34, 0, self.playback_controls.height - self.playback_controls.window_height),
        )

    def render_track_statuses(self) -> None:
        ts_df = self.data_extractor.track_statuses(self.width)

        for record in ts_df.itertuples():
            DirectFrame(
                parent=self.timeline_frame,
                frameColor=record.Color,
                frameSize=(0, record.Width, 0, -self.height),
                pos=Point3(record.PixelStart, 0, 0),
            )

    def render(self) -> None:
        self.render_timeline_frame()
        self.render_track_statuses()
