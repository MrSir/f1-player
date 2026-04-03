import math

from pandas import DataFrame
from pandas._testing import assert_frame_equal

from f1p.utils.geometry import center_pos_data, find_center, resize_pos_data, rotate, scale, shift


def test_scale() -> None:
    df = DataFrame(
        {
            "X": [1.0, 2.0, 3.0],
            "Y": [10.0, 20.0, 30.0],
            "Z": [100.0, 200.0, 300.0],
        }
    )

    expected = DataFrame(
        {
            "X": [2.0, 4.0, 6.0],
            "Y": [20.0, 40.0, 60.0],
            "Z": [200.0, 400.0, 600.0],
        }
    )

    assert_frame_equal(expected, scale(df, 2))


def test_shift() -> None:
    df = DataFrame(
        {
            "X": [1.0, 2.0, 3.0],
            "Y": [10.0, 20.0, 30.0],
            "Z": [100.0, 200.0, 300.0],
        }
    )

    expected = DataFrame(
        {
            "X": [11.0, 12.0, 13.0],
            "Y": [10.0, 20.0, 30.0],
            "Z": [100.0, 200.0, 300.0],
        }
    )

    assert_frame_equal(expected, shift(df, "X", 10))


def test_rotate() -> None:
    df = DataFrame(
        {
            "X": [1.0, 1.0, 1.0],
            "Y": [1.0, 1.0, 1.0],
            "Z": [1.0, 1.0, 1.0],
        }
    )

    expected = DataFrame(
        {
            "X": [-0.3660254037844385, -0.3660254037844385, -0.3660254037844385],
            "Y": [1.3660254037844388, 1.3660254037844388, 1.3660254037844388],
            "Z": [1.0, 1.0, 1.0],
        }
    )

    assert_frame_equal(expected, rotate(df, math.pi / 3))


def test_find_center() -> None:
    df = DataFrame(
        {
            "X": [1.0, 2.0, 3.0],
            "Y": [10.0, 20.0, 30.0],
            "Z": [100.0, 200.0, 300.0],
        }
    )

    expected = (2.0, 20.0, 200.0)

    assert expected == find_center(df)


def test_resize_pos_data() -> None:
    df = DataFrame(
        {
            "X": [1.0, 1.0, 1.0],
            "Y": [1.0, 1.0, 1.0],
            "Z": [1.0, 1.0, 1.0],
        }
    )

    expected = DataFrame(
        {
            "X": [-0.0006100423396407309, -0.0006100423396407309, -0.0006100423396407309],
            "Y": [0.002276709006307398, 0.002276709006307398, 0.002276709006307398],
            "Z": [0.0016666666666666668, 0.0016666666666666668, 0.0016666666666666668],
        }
    )

    assert_frame_equal(expected, resize_pos_data(math.pi / 3, df))


def test_center_pos_data() -> None:
    df = DataFrame(
        {
            "X": [1.0, 2.0, 3.0],
            "Y": [10.0, 20.0, 30.0],
            "Z": [100.0, 200.0, 300.0],
        }
    )

    expected = DataFrame(
        {
            "X": [-1.0, 0.0, 1.0],
            "Y": [-10.0, 0.0, 10.0],
            "Z": [-100.0, 0.0, 100.0],
        }
    )

    assert_frame_equal(expected, center_pos_data((2.0, 20.0, 200.0), df))
