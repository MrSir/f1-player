from unittest.mock import MagicMock

import pandas as pd
import pytest
from fastf1.core import Session
from fastf1.mvapi import CircuitInfo
from panda3d.core import LVecBase4f, deg2Rad
from pandas import DataFrame, Series, Timedelta
from pytest_mock import MockerFixture

from f1p.services.data_extractor.track_statuses import (
    GreenFlagTrackStatus,
    RedFlagTrackStatus,
    SafetyCarTrackStatus,
    VSCDeployedTrackStatus,
    VSCEndingTrackStatus,
    YellowFlagTrackStatus,
)


@pytest.fixture()
def corners() -> DataFrame:
    return DataFrame(
        {
            "X": [1, 2, 3, 4, 5],
            "Y": [1, 2, 3, 4, 5],
            "Number": [1, 2, 2, 3, 4],
            "Letter": ["", "a", "b", "", ""],
            "Angle": [5, 10, 15, 20, 25],
            "Distance": [10, 20, 30, 40, 50],
        },
    )


@pytest.fixture()
def circuit_info(corners: DataFrame) -> CircuitInfo:
    return CircuitInfo(
        corners=corners,
        marshal_lights=DataFrame(),
        marshal_sectors=DataFrame(),
        rotation=45.0,
    )


@pytest.fixture()
def session_start_time() -> Timedelta:
    return Timedelta(milliseconds=1001)


@pytest.fixture()
def session_end_time() -> Timedelta:
    return Timedelta(milliseconds=4001)


@pytest.fixture()
def track_status() -> DataFrame:
    return DataFrame(
        {
            "Status": ["1", "2", "1"],
            "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000), Timedelta(milliseconds=4000)],
        },
    )


@pytest.fixture()
def track_status_colors() -> DataFrame:
    return pd.DataFrame(
        data=[
            GreenFlagTrackStatus(),
            YellowFlagTrackStatus(),
            SafetyCarTrackStatus(),
            RedFlagTrackStatus(),
            VSCDeployedTrackStatus(),
            VSCEndingTrackStatus(),
        ],
    )


@pytest.fixture()
def weather_data() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=1000),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
                Timedelta(milliseconds=5000),
            ],
            "AirTemp": [21.0, 23.0, 25.0, 16.0, 15.0],
            "Humidity": [80.0, 50.0, 0.0, 0.0, 0.0],
            "Pressure": [1024.6, 1024.6, 1031.6, 1018.4, 1024.6],
            "Rainfall": [True, True, False, False, False],
            "TrackTemp": [45.0, 46.0, 47.0, 48.0, 60.0],
            "WindDirection": [91, 116, 99, 300, 65],
            "WindSpeed": [2.1, 1.5, 2.0, 1.8, 2.7],
        },
    )


@pytest.fixture()
def mock_session(
    circuit_info: CircuitInfo,
    track_status: DataFrame,
    weather_data: DataFrame,
    mocker: MockerFixture,
) -> MagicMock:
    session = mocker.MagicMock(spec=Session)
    session.get_circuit_info = mocker.MagicMock(return_value=circuit_info)
    session.track_status = track_status
    session.weather_data = weather_data

    return session


@pytest.fixture()
def processed_corners() -> DataFrame:
    return DataFrame(
        {
            "X": [-1.2, -1.2, -1.2, -1.2, -1.2],
            "Y": [-1.297643, -1.295286, -1.292929, -1.290572, -1.288215],
            "Number": [1, 2, 2, 3, 4],
            "Letter": ["", "a", "b", "", ""],
            "Angle": [5, 10, 15, 20, 25],
            "Distance": [10, 20, 30, 40, 50],
            "Label": ["1", "2a", "2b", "3", "4"],
            "AngleRad": [deg2Rad(5), deg2Rad(10), deg2Rad(15), deg2Rad(20), deg2Rad(25)],
            "Z": [1, 1, 1, 1, 1],
        },
    )


@pytest.fixture()
def session_time_ticks_df() -> DataFrame:
    return DataFrame(
        {
            "SessionTime": [
                Timedelta(milliseconds=1000),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
                Timedelta(milliseconds=5000),
            ],
            "SessionTimeTick": [1, 2, 3, 4, 5],
        },
    )


@pytest.fixture()
def augmented_session_time_ticks_df() -> DataFrame:
    return DataFrame(
        {
            "SessionTime": [
                Timedelta(milliseconds=1000),
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
                Timedelta(milliseconds=5000),
            ],
            "SessionTimeTick": [1, 2, 3, 4, 5],
            "Pixel": [
                0.0,
                20.0,
                40.0,
                60.0,
                80.0,
            ],
        },
    )


@pytest.fixture()
def processed_track_statuses_after_trim_to_session_time(session_end_time) -> DataFrame:
    return DataFrame(
        {
            "Status": ["2", "1"],
            "Time": [Timedelta(milliseconds=2000), Timedelta(milliseconds=4000)],
            "EndTime": [Timedelta(milliseconds=4000), session_end_time],
        },
    )


@pytest.fixture()
def processed_track_statuses_after_add_session_time_ticks(session_end_time) -> DataFrame:
    return DataFrame(
        {
            "Status": ["2", "1"],
            "Time": [Timedelta(milliseconds=2000), Timedelta(milliseconds=4000)],
            "EndTime": [Timedelta(milliseconds=4000), session_end_time],
            "SessionTimeTick": [2, 4],
            "SessionTimeTickEnd": [4, 4],
        },
    )


@pytest.fixture()
def processed_track_statuses_after_merge_augmented_session_time_ticks() -> DataFrame:
    return DataFrame(
        {
            "Status": ["2", "1"],
            "SessionTimeTick": [2, 4],
            "SessionTimeTickEnd": [4, 4],
            "PixelStart": [20.0, 60.0],
            "PixelEnd": [60.0, 60.0],
        },
    )


@pytest.fixture()
def processed_track_statuses_after_compute_width() -> DataFrame:
    return DataFrame(
        {
            "Status": ["2", "1"],
            "SessionTimeTick": [2, 4],
            "SessionTimeTickEnd": [4, 4],
            "PixelStart": [20.0, 60.0],
            "PixelEnd": [60.0, 60.0],
            "Width": [40.0, 0.0],
        },
    )


@pytest.fixture()
def processed_track_statuses_after_convert_status_to_int() -> DataFrame:
    return DataFrame(
        {
            "Status": [2, 1],
            "SessionTimeTick": [2, 4],
            "SessionTimeTickEnd": [4, 4],
            "PixelStart": [20.0, 60.0],
            "PixelEnd": [60.0, 60.0],
            "Width": [40.0, 0.0],
        },
    )


@pytest.fixture()
def processed_track_statuses() -> DataFrame:
    return DataFrame(
        {
            "Status": [2, 1],
            "SessionTimeTick": [2, 4],
            "SessionTimeTickEnd": [4, 4],
            "PixelStart": [20.0, 60.0],
            "PixelEnd": [60.0, 60.0],
            "Width": [40.0, 0.0],
            "Label": ["Yellow Flag", "Green Flag"],
            "Color": [LVecBase4f(1, 1, 0, 0.8), LVecBase4f(0, 1, 0, 0.8)],
            "TextColor": [LVecBase4f(0, 0, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
        },
    )


@pytest.fixture()
def processed_weather_data_after_trim_to_session_time() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [1024.6, 1031.6, 1018.4],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [1.5, 2.0, 1.8],
        },
    )


@pytest.fixture()
def processed_weather_data_after_add_session_time_ticks() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [1024.6, 1031.6, 1018.4],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [1.5, 2.0, 1.8],
            "SessionTimeTick": [2, 3, 4],
        },
    )


@pytest.fixture()
def processed_weather_data_after_convert_air_temp_to_fahrenheit() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [1024.6, 1031.6, 1018.4],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [1.5, 2.0, 1.8],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
        },
    )


@pytest.fixture()
def processed_weather_data_after_convert_track_temp_to_fahrenheit() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [1024.6, 1031.6, 1018.4],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [1.5, 2.0, 1.8],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
        },
    )


@pytest.fixture()
def processed_weather_data_after_convert_pressure_to_kilopascal() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [1.5, 2.0, 1.8],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
        },
    )


@pytest.fixture()
def processed_weather_data_after_convert_wind_speed_to_km_p_h() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [5.4, 7.2, 6.4799999999999995],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
        },
    )


@pytest.fixture()
def processed_weather_data_after_add_weather_symbol() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [5.4, 7.2, 6.4799999999999995],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
            "WeatherSymbol": ["🌧", "🌣", "🌣"],
        },
    )


@pytest.fixture()
def processed_weather_data_after_add_weather_text() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [5.4, 7.2, 6.4799999999999995],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
            "WeatherSymbol": ["🌧", "🌣", "🌣"],
            "WeatherText": ["RAIN", "SUNNY", "SUNNY"],
        },
    )


@pytest.fixture()
def processed_weather_data_after_add_wind_direction_symbol() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [5.4, 7.2, 6.4799999999999995],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
            "WeatherSymbol": ["🌧", "🌣", "🌣"],
            "WeatherText": ["RAIN", "SUNNY", "SUNNY"],
            "WindDirectionSymbol": ["🢄", "🢀", "🢆"],
        },
    )


@pytest.fixture()
def processed_weather_data() -> DataFrame:
    return DataFrame(
        {
            "Time": [
                Timedelta(milliseconds=2000),
                Timedelta(milliseconds=3000),
                Timedelta(milliseconds=4000),
            ],
            "AirTemp": [23.0, 25.0, 16.0],
            "Humidity": [50.0, 0.0, 0.0],
            "Pressure": [102.46, 103.16, 101.84],
            "Rainfall": [True, False, False],
            "TrackTemp": [46.0, 47.0, 48.0],
            "WindDirection": [116, 99, 300],
            "WindSpeed": [5.4, 7.2, 6.4799999999999995],
            "SessionTimeTick": [2, 3, 4],
            "AirTempF": [73.4, 77.0, 60.8],
            "TrackTempF": [114.8, 116.6, 118.4],
            "WeatherSymbol": ["🌧", "🌣", "🌣"],
            "WeatherText": ["RAIN", "SUNNY", "SUNNY"],
            "WindDirectionSymbol": ["🢄", "🢀", "🢆"],
            "WindDirectionText": ["SOUTH EAST", "EAST", "NORTH WEST"],
        },
    )


@pytest.fixture()
def processed_weather_data_at_tick_2() -> Series:
    return Series(
        [
            Timedelta(milliseconds=2000),
            23.0,
            50.0,
            102.46,
            True,
            46.0,
            116,
            5.4,
            2,
            73.4,
            114.8,
            "🌧",
            "RAIN",
            "🢄",
            "SOUTH EAST",
        ],
        index=[
            "Time",
            "AirTemp",
            "Humidity",
            "Pressure",
            "Rainfall",
            "TrackTemp",
            "WindDirection",
            "WindSpeed",
            "SessionTimeTick",
            "AirTempF",
            "TrackTempF",
            "WeatherSymbol",
            "WeatherText",
            "WindDirectionSymbol",
            "WindDirectionText",
        ],
        name=0,
    )


#
# @pytest.fixture()
# def mock_parent(mocker: MockerFixture) -> MagicMock:
#     return mocker.MagicMock(spec=NodePath)
#
#
# @pytest.fixture()
# def mock_task_manager(mocker: MockerFixture) -> MagicMock:
#     return mocker.MagicMock(spec=TaskManager)
#
#
# @pytest.fixture()
# def mock_text_font(mocker: MockerFixture) -> MagicMock:
#     return mocker.MagicMock(spec=StaticTextFont)
#
#
# @pytest.fixture()
# def data_extractor_service(
#         mock_parent: MagicMock,
#         mock_task_manager: MagicMock,
#         mock_text_font: MagicMock,
#         mocker: MockerFixture,
# ) -> DataExtractorService:
#     mocker.patch.object(DataExtractorService, "accept")
#     mocker.patch("f1p.services.data_extractor.service.fastf1.Cache.enable_cache")
#
#     service = DataExtractorService(
#         parent=mock_parent,
#         task_manager=mock_task_manager,
#         window_width=1920,
#         window_height=1080,
#         text_font=mock_text_font,
#     )
#     service.year = 2024
#     service.event_name = "Bahrain"
#     service.session_id = "FP1"
#
#     return service
#
#
# @pytest.fixture()
# def mock_session_status() -> DataFrame:
#     return pd.DataFrame({
#         "Status": ["Started", "Finalised"],
#         "Time": [Timedelta(milliseconds=1000), Timedelta(milliseconds=5000)],
#     })
#
#
# @pytest.fixture()
# def mock_processed_pos_data() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTimeTick": [1, 2, 3, 4, 5],
#         "LapsCompletion": [0.5, 1.2, 1.8, 2.1, 2.9],
#         "Z": [0.0, 1.5, 2.0, 1.8, 0.5],
#         "DriverNumber": [1, 1, 2, 2, 1],
#     })
#

# @pytest.fixture()
# def green_flag_track_status() -> DataFrame:
#     return pd.DataFrame({
#         "Status": [1],
#         "Label": ["Green Flag"],
#         "Color": [LVecBase4f(0, 1, 0, 0.8)],
#         "TextColor": [LVecBase4f(0, 0, 0, 0.8)],
#     })
#
#
# @pytest.fixture()
# def processed_weather_data() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTimeTick": [1, 2, 3, 4, 5],
#         "Time": [
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=3000),
#             Timedelta(milliseconds=4000),
#             Timedelta(milliseconds=5000),
#         ],
#         "AirTemp": [20, 21, 22, 21, 20],
#         "TrackTemp": [30, 31, 32, 31, 30],
#     })
#
#
# @pytest.fixture()
# def processed_track_statuses() -> DataFrame:
#     return pd.DataFrame({
#         "Status": [1, 2],
#         "SessionTimeTick": [1, 2],
#         "SessionTimeTickEnd": [2, 4],
#         "PixelStart": [0, 166.666667],
#         "PixelEnd": [166.666667, 500],
#         "Width": [166.666667, 333.333333],
#         "Label": ["Green Flag", "Yellow Flag"],
#         "Color": [LVecBase4f(0, 1, 0, 0.8), LVecBase4f(1, 1, 0, 0.8)],
#         "TextColor": [LVecBase4f(0, 0, 0, 0.8), LVecBase4f(0, 0, 0, 0.8)],
#     })
#
#
# @pytest.fixture()
# def mock_pos_data_with_session_time() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTimeTick": [1, 2, 3, 4, 1, 2, 3],
#         "SessionTime": [
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=3000),
#             Timedelta(milliseconds=4000),
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=3000),
#         ],
#         "X": [1.0, 2.0, 3.0, 4.0, 1.1, 2.1, 3.1],
#         "Y": [1.0, 2.0, 3.0, 4.0, 1.1, 2.1, 3.1],
#         "Z": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         "DriverNumber": [1, 1, 1, 1, 2, 2, 2],
#     })
#
#
# @pytest.fixture()
# def fastest_lap_data() -> DataFrame:
#     return pd.DataFrame({
#         "X": [1.0, 2.0, 3.0, 4.0],
#         "Y": [1.0, 2.0, 3.0, 4.0],
#         "Z": [0.0, 0.0, 0.0, 0.0],
#     })
#
#
# @pytest.fixture()
# def pos_data_dict(mocker: MockerFixture, fastest_lap_data: DataFrame) -> dict[str, Telemetry]:
#     mock_telemetry_1 = mocker.MagicMock(spec=Telemetry)
#     mock_telemetry_1.__getitem__ = lambda key: fastest_lap_data[key]
#     mock_telemetry_1.columns = fastest_lap_data.columns.tolist()
#
#     mock_telemetry_2 = mocker.MagicMock(spec=Telemetry)
#     mock_telemetry_2.__getitem__ = lambda key: fastest_lap_data[key]
#     mock_telemetry_2.columns = fastest_lap_data.columns.tolist()
#
#     return {"1": mock_telemetry_1, "2": mock_telemetry_2}
#
#
# @pytest.fixture()
# def pos_data_for_filtering() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTime": [
#             Timedelta(milliseconds=500),
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=1500),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=2500),
#         ],
#         "X": [1.0, 2.0, 3.0, 4.0, 5.0],
#         "Y": [1.0, 2.0, 3.0, 4.0, 5.0],
#         "Z": [0.0, 0.0, 0.0, 0.0, 0.0],
#         "DriverNumber": [1, 1, 1, 1, 1],
#     })
#
#
# @pytest.fixture()
# def pos_data_for_normalization() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTime": [Timedelta(milliseconds=1000), Timedelta(milliseconds=2000)],
#         "X": [1.0, 2.0],
#         "Y": [1.0, 2.0],
#         "Z": [0.0, 0.0],
#         "DriverNumber": [1, 1],
#     })
#
#
# @pytest.fixture()
# def pos_data_for_milliseconds() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTime": [
#             Timedelta(seconds=1),
#             Timedelta(seconds=2),
#             Timedelta(seconds=3),
#         ],
#         "X": [1.0, 2.0, 3.0],
#         "Y": [1.0, 2.0, 3.0],
#         "Z": [0.0, 0.0, 0.0],
#         "DriverNumber": [1, 1, 1],
#     })
#
#
# @pytest.fixture()
# def pos_data_for_session_time_tick() -> DataFrame:
#     return pd.DataFrame({
#         "SessionTime": [
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=3000),
#             Timedelta(milliseconds=1000),
#             Timedelta(milliseconds=2000),
#             Timedelta(milliseconds=3000),
#         ],
#         "X": [1.0, 2.0, 3.0, 1.1, 2.1, 3.1],
#         "Y": [1.0, 2.0, 3.0, 1.1, 2.1, 3.1],
#         "Z": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
#         "DriverNumber": [1, 1, 1, 2, 2, 2],
#     })
#
#
# @pytest.fixture()
# def laps_df() -> DataFrame:
#     return DataFrame(
#         data={
#             "DriverNumber": [1, 1, 1, 1, 1],
#             "LapNumber": [1, 2, 3, 4, 5],
#             "LapTime": [
#                 pd.NaT,
#                 timedelta(milliseconds=0),
#                 timedelta(minutes=1, seconds=32, milliseconds=50),
#                 timedelta(minutes=1, seconds=32, milliseconds=400),
#                 timedelta(minutes=1, seconds=32, milliseconds=450),
#             ],
#             "LapTimeMilliseconds": [
#                 pd.NA,
#                 0,
#                 92050,
#                 92400,
#                 92450,
#             ],
#         },
#     )
#
#
# @pytest.fixture()
# def fastest_lap() -> Series:
#     return Series(
#         [1, 3, timedelta(minutes=1, seconds=32, milliseconds=50), 92050],
#         index=[
#             "DriverNumber",
#             "LapNumber",
#             "LapTime",
#             "LapTimeMilliseconds",
#         ],
#     )
