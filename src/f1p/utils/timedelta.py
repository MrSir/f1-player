from datetime import timedelta


def td_to_min_n_sec(td: timedelta) -> str:
    total_seconds = td.total_seconds()
    minutes = total_seconds // 60
    seconds = total_seconds % 60

    return "{:01.0f}:{:02.3f}".format(minutes, seconds)
