from pandas import DataFrame, Timedelta
from pandas._testing import assert_frame_equal

from f1p.utils.dataframe import merge_in_session_time_ticks


def test_merge_in_session_time_ticks(session_time_ticks_df: DataFrame) -> None:
    target_df = DataFrame(
        {
            "SessionTime": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
        }
    )

    expected_df = DataFrame(
        {
            "SessionTime": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
            "SessionTimeTick": [1, 2, 3, 4, 5],
        }
    )

    assert_frame_equal(expected_df, merge_in_session_time_ticks(target_df, session_time_ticks_df))


def test_merge_in_session_time_ticks_with_comparison_column(session_time_ticks_df: DataFrame) -> None:
    target_df = DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
        }
    )

    expected_df = DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
            "SessionTimeTick": [1, 2, 3, 4, 5],
        }
    )

    assert_frame_equal(
        expected_df,
        merge_in_session_time_ticks(target_df, session_time_ticks_df, target_df_comparison_column="Time")
    )


def test_merge_in_session_time_ticks_with_target_df_result_column(session_time_ticks_df: DataFrame) -> None:
    target_df = DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
        }
    )

    expected_df = DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=1010),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3040),
                Timedelta(milliseconds=4050),
                Timedelta(milliseconds=5000),
            ],
            "A": [1, 2, 3, 4, 5],
            "B": [6, 7, 8, 9, 10],
            "Tick": [1, 2, 3, 4, 5],
        }
    )

    assert_frame_equal(
        expected_df,
        merge_in_session_time_ticks(
            target_df,
            session_time_ticks_df,
            target_df_comparison_column="Time",
            target_df_result_column="Tick",
        )
    )
