from datetime import timedelta

import pytest
from pandas import Series
from pandas._testing import assert_series_equal

from f1p.utils.timedelta import td_series_to_min_n_sec, td_to_min_n_sec


def test_td_to_min_n_sec_returns_early_when_not_timedelta() -> None:
    assert "N/A" == td_to_min_n_sec("not a timedelta")


@pytest.mark.parametrize(
    ("td", "expected"),
    [
        (timedelta(minutes=1, seconds=23, milliseconds=456), "1:23.456"),
        (timedelta(minutes=0, seconds=23, milliseconds=456), "0:23.456"),
        (timedelta(minutes=0, seconds=3, milliseconds=456), "0:03.456"),
    ]
)
def test_td_to_min_n_sec(td: timedelta, expected: str) -> None:
    assert expected == td_to_min_n_sec(td)


@pytest.mark.parametrize(
    ("input", "output"),
    [
        (Series(83456), Series("1:23.456")),
        (Series(23456), Series("0:23.456")),
        (Series(3456), Series("0:03.456")),
    ]
)
def test_td_series_to_min_n_sec(input: Series, output: Series) -> None:
    assert_series_equal(output, td_series_to_min_n_sec(input))
