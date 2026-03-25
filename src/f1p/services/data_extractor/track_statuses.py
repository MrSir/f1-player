from panda3d.core import LVecBase4f
from pandas import Series


class GreenFlagTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [1, "Green Flag", LVecBase4f(0, 1, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )


class YellowFlagTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [2, "Yellow Flag", LVecBase4f(1, 1, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )


class SafetyCarTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [4, "Safety Car", LVecBase4f(1, 1, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )


class RedFlagTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [5, "Red Flag", LVecBase4f(1, 0, 0, 0.8), LVecBase4f(1, 1, 1, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )


class VSCDeployedTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [6, "VSC Deployed", LVecBase4f(1, 0.64, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )


class VSCEndingTrackStatus(Series):
    def __init__(self):
        super().__init__(
            [7, "VSC Ending", LVecBase4f(1, 0.64, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
            index=["Status", "Label", "Color", "TextColor"]
        )
