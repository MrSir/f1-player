import numpy as np
from pandas import DataFrame


def scale(df: DataFrame, factor: float) -> DataFrame:
    new_df = df.copy()
    new_df["X"] = new_df["X"] * factor
    new_df["Y"] = new_df["Y"] * factor
    new_df["Z"] = new_df["Z"] * factor

    return new_df

def shift(df: DataFrame, direction: str, amount: float) -> DataFrame:
    new_df = df.copy()
    new_df[direction] = new_df[direction] + amount

    return new_df


def rotate(df: DataFrame, radians: float) -> DataFrame:
    coordinates = df.loc[:, ('X', 'Y', 'Z')].to_numpy()

    rot_mat = np.array(
        [
            [np.cos(radians), np.sin(radians), 0],
            [-np.sin(radians), np.cos(radians), 0],
            [0, 0, 1],
        ]
    )
    rotated_coordinates = np.matmul(coordinates, rot_mat)

    return DataFrame(
        data={
            "X": rotated_coordinates[:, 0],
            "Y": rotated_coordinates[:, 1],
            "Z": rotated_coordinates[:, 2],
        }
    )

def find_center(df: DataFrame) -> list[float]:
    return [
        ((df["X"].max() - df["X"].min()) / 2) + df["X"].min(),
        ((df["Y"].max() - df["Y"].min()) / 2) + df["Y"].min(),
        ((df["Z"].max() - df["Z"].min()) / 2) + df["Z"].min(),
    ]