from panda3d.core import LVecBase4f
from pandas import Series

from f1p.services.data_extractor.track_statuses import GreenFlagTrackStatus, YellowFlagTrackStatus, \
    SafetyCarTrackStatus, VSCDeployedTrackStatus, VSCEndingTrackStatus, RedFlagTrackStatus


def test_green_flag_track_status() -> None:
    status = GreenFlagTrackStatus()

    assert isinstance(status, Series)
    assert 1 == status["Status"]
    assert "Green Flag" == status["Label"]
    assert LVecBase4f(0, 1, 0, 0.8) == status["Color"]
    assert LVecBase4f(0, 0, 0, 0.8) == status["TextColor"]


def test_yellow_flag_track_status() -> None:
    status = YellowFlagTrackStatus()

    assert isinstance(status, Series)
    assert 2 == status["Status"]
    assert "Yellow Flag" == status["Label"]
    assert LVecBase4f(1, 1, 0, 0.8) == status["Color"]
    assert LVecBase4f(0, 0, 0, 0.8) == status["TextColor"]


def test_safety_car_track_status() -> None:
    status = SafetyCarTrackStatus()

    assert isinstance(status, Series)
    assert 4 == status["Status"]
    assert "Safety Car" == status["Label"]
    assert LVecBase4f(1, 1, 0, 0.8) == status["Color"]
    assert LVecBase4f(0, 0, 0, 0.8) == status["TextColor"]


def test_red_flag_track_status() -> None:
    status = RedFlagTrackStatus()

    assert isinstance(status, Series)
    assert 5 == status["Status"]
    assert "Red Flag" == status["Label"]
    assert LVecBase4f(1, 0, 0, 0.8) == status["Color"]
    assert LVecBase4f(1, 1, 1, 0.8) == status["TextColor"]


def test_vsc_deployed_track_status() -> None:
    status = VSCDeployedTrackStatus()

    assert isinstance(status, Series)
    assert 6 == status["Status"]
    assert "VSC Deployed" == status["Label"]
    assert LVecBase4f(1, 0.64, 0, 0.8) == status["Color"]
    assert LVecBase4f(0, 0, 0, 0.8) == status["TextColor"]


def test_vsc_ending_track_status() -> None:
    status = VSCEndingTrackStatus()

    assert isinstance(status, Series)
    assert 7 == status["Status"]
    assert "VSC Ending" == status["Label"]
    assert LVecBase4f(1, 0.64, 0, 0.8) == status["Color"]
    assert LVecBase4f(0, 0, 0, 0.8) == status["TextColor"]
