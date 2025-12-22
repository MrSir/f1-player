from direct.gui.DirectButton import DirectButton
from direct.gui.DirectGuiGlobals import RAISED


class BlackButton(DirectButton):
    def __init__(self, parent=None, **kwargs):
        default_options = (
            ("frameColor", (0.1, 0.1, 0.1, 1), None),
            ("relief", RAISED, None),
            ("borderWidth", (3, 3), None),
            ("pressEffect", 1, None),
            ("text_fg", (1, 1, 1, 1), None),
        )
        self.defineoptions(kwargs, default_options)

        DirectButton.__init__(self, parent, **kwargs)

        self.initialiseoptions(BlackButton)