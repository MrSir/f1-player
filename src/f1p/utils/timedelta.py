from datetime import timedelta
from math import floor


def td_to_min_n_sec(td: timedelta) -> str:
    if not isinstance(td, timedelta):
        return "N/A"

    total_seconds = td.total_seconds()
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    milliseconds = (seconds - floor(seconds)) * 1000

    return "{:01d}:{:02d}.{}".format(int(minutes), int(seconds), int(milliseconds))
