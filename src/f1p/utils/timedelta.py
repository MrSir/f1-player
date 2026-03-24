from datetime import timedelta

from pandas import Series


def td_to_min_n_sec(td: timedelta) -> str:
    if not isinstance(td, timedelta):
        return "N/A"

    total_seconds = td.total_seconds()
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return "{:01}:{:06.3f}".format(int(minutes), seconds)


def td_series_to_min_n_sec(sr: Series) -> Series:
    minutes_sr = sr // 60000
    seconds_sr = (sr % 60000) / 1000

    return minutes_sr.fillna(0).astype(int).map("{:01}".format) + ":" + seconds_sr.fillna(0).map("{:06.3f}".format)
