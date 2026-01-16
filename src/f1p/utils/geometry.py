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
    coordinates = df.loc[:, ("X", "Y", "Z")].to_numpy()

    rot_mat = np.array(
        [
            [np.cos(radians), np.sin(radians), 0],
            [-np.sin(radians), np.cos(radians), 0],
            [0, 0, 1],
        ],
    )
    rotated_coordinates = np.matmul(coordinates, rot_mat)

    return DataFrame(
        data={
            "X": rotated_coordinates[:, 0],
            "Y": rotated_coordinates[:, 1],
            "Z": rotated_coordinates[:, 2],
        },
    )


def find_center(df: DataFrame) -> tuple[float, float, float]:
    return (
        ((df["X"].max() - df["X"].min()) / 2) + df["X"].min(),
        ((df["Y"].max() - df["Y"].min()) / 2) + df["Y"].min(),
        ((df["Z"].max() - df["Z"].min()) / 2) + df["Z"].min(),
    )


def resize_pos_data(rotation: float, pos_data_df: DataFrame) -> DataFrame:
    df = pos_data_df.copy()

    coordinates_cols_only_df = df[["X", "Y", "Z"]]
    rotated_coordinates_df = rotate(coordinates_cols_only_df, rotation)

    scaled_coordinates_df = scale(rotated_coordinates_df, 1 / 600)

    df["X"] = scaled_coordinates_df["X"].to_numpy()
    df["Y"] = scaled_coordinates_df["Y"].to_numpy()
    df["Z"] = scaled_coordinates_df["Z"].to_numpy()

    return df


def center_pos_data(map_center_coordinate: tuple[float, float, float], df: DataFrame) -> DataFrame:
    combined_pos_data_df = df.copy()
    coordinates_cols_only_df = combined_pos_data_df[["X", "Y", "Z"]]

    shifted_x_coordinates_df = shift(coordinates_cols_only_df, direction="X", amount=-map_center_coordinate[0])
    shifted_y_coordinates_df = shift(coordinates_cols_only_df, direction="Y", amount=-map_center_coordinate[1])
    shifted_z_coordinates_df = shift(coordinates_cols_only_df, direction="Z", amount=-map_center_coordinate[2])

    combined_pos_data_df["X"] = shifted_x_coordinates_df["X"].to_numpy()
    combined_pos_data_df["Y"] = shifted_y_coordinates_df["Y"].to_numpy()
    combined_pos_data_df["Z"] = shifted_z_coordinates_df["Z"].to_numpy()

    return combined_pos_data_df
