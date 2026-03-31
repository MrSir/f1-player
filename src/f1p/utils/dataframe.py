import numpy as np
from pandas import DataFrame


def merge_in_session_time_ticks(
    target_df: DataFrame,
    session_time_ticks_df: DataFrame,
    target_df_comparison_column: str = "SessionTime",
    target_df_result_column: str = "SessionTimeTick",
) -> DataFrame:
    df = target_df.copy()

    ticks_df_sorted = (
        session_time_ticks_df.groupby("SessionTime", sort=True)["SessionTimeTick"]
        .max()
        .reset_index()
        .sort_values(
            "SessionTime",
        )
    )
    times = ticks_df_sorted["SessionTime"].values  # sorted datetime64 array
    ticks = ticks_df_sorted["SessionTimeTick"].values
    indices = np.searchsorted(times, df[target_df_comparison_column].values, side="right") - 1
    valid = indices >= 0
    result = np.where(valid, ticks[np.clip(indices, 0, len(ticks) - 1)], np.nan)

    df[target_df_result_column] = result

    # Remove rows that have no time tick matched to them.
    # Could happen if the session_start_time is earlier than the Session Time on tick number 1
    df = df.dropna(subset=[target_df_result_column])

    df.loc[:,target_df_result_column] = df[target_df_result_column].astype("int64")

    return df
