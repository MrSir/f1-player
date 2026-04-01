from typing import cast
from unittest.mock import MagicMock

import pandas as pd
import pytest
from pandas import DataFrame, Series
from pandas._testing import assert_frame_equal, assert_series_equal
from pytest_mock import MockerFixture

from f1p.services.data_extractor.enums import ConventionalSessionIdentifiers, SprintQualifyingSessionIdentifiers
from f1p.services.data_extractor.parsers.session import SessionParser


@pytest.fixture()
def parser() -> SessionParser:
    return SessionParser()


def test_initialization() -> None:
    parser = SessionParser()

    assert parser._year is None
    assert parser._event_name is None
    assert parser._session_id is None

    assert parser._event_schedule is None
    assert parser._event is None
    assert parser._session is None

    assert parser._session_status is None
    assert parser._session_start_time is None
    assert parser._session_end_time is None

    assert parser._session_results is None
    assert parser._total_laps is None


def test_year_property_returns_set_value(parser: SessionParser) -> None:
    year = 2026
    parser._year = year

    assert year == parser.year


def test_year_property_raises_value_error_when_none(parser: SessionParser) -> None:
    assert parser._year is None

    with pytest.raises(ValueError, match="Year not set"):
        assert parser.year is None


def test_year_setter(parser: SessionParser) -> None:
    year = 2026
    parser.year = year

    assert year == parser._year


def test_event_name_property_returns_set_value(parser: SessionParser) -> None:
    event_name = "Monaco Grand Prix"
    parser._event_name = event_name

    assert event_name == parser.event_name


def test_event_name_property_raises_value_error_when_none(parser: SessionParser) -> None:
    assert parser._event_name is None

    with pytest.raises(ValueError, match="Event name not set"):
        assert parser.event_name is None


def test_event_name_setter(parser: SessionParser) -> None:
    event_name = "Monaco Grand Prix"
    parser.event_name = event_name

    assert event_name == parser._event_name
    

def test_session_id_property_returns_set_value(parser: SessionParser) -> None:
    session_id = "Race"
    parser._session_id = session_id

    assert session_id == parser.session_id


def test_session_id_property_raises_value_error_when_none(parser: SessionParser) -> None:
    assert parser._session_id is None

    with pytest.raises(ValueError, match="Session id not set"):
        assert parser.session_id is None


def test_session_id_setter(parser: SessionParser) -> None:
    session_id = "Race"
    parser.session_id = session_id

    assert session_id == parser._session_id


def test_event_schedule_property_computes_when_none(
    parser: SessionParser,
    event_schedule: DataFrame,
    mocker: MockerFixture,
) -> None:
    assert parser._event_schedule is None

    year = 2026
    parser._year = year
    mock_get_event_schedule = mocker.MagicMock(return_value=event_schedule)
    mocker.patch("f1p.services.data_extractor.parsers.session.fastf1.get_event_schedule", mock_get_event_schedule)

    assert_frame_equal(event_schedule, parser.event_schedule)

    assert parser._event_schedule is not None
    assert_frame_equal(event_schedule, parser._event_schedule)

    mock_get_event_schedule.assert_called_once_with(year)


def test_event_schedule_property_caches(
    parser: SessionParser,
    event_schedule: DataFrame,
    mocker: MockerFixture,
) -> None:
    assert parser._event_schedule is None

    year = 2026
    parser._year = year
    mock_get_event_schedule = mocker.MagicMock(return_value=event_schedule)
    mocker.patch("f1p.services.data_extractor.parsers.session.fastf1.get_event_schedule", mock_get_event_schedule)

    assert_frame_equal(event_schedule, parser.event_schedule), "First time computes"
    assert_frame_equal(event_schedule, parser.event_schedule), "Second time returns cachee"

    mock_get_event_schedule.assert_called_once_with(year)


def test_race_event_names_property_when_year_is_none(parser: SessionParser) -> None:
    assert parser._year is None

    assert ["Event"] == parser.race_event_names


def test_race_event_names_selects_race_events(
    parser: SessionParser,
    event_schedule: DataFrame,
    race_event_schedule: DataFrame,
) -> None:
    year = 2026
    parser._year = year
    parser._event_schedule = event_schedule

    expected = ["Event"] + race_event_schedule["EventName"].tolist()

    assert expected == parser.race_event_names


def test_event_property_computes_when_none(    parser: SessionParser,    event_schedule: DataFrame) -> None:
    event_name = "Australian Grand Prix"
    parser._event_name = event_name
    parser._event_schedule = event_schedule

    expected = event_schedule[event_schedule["EventName"] == event_name].iloc[0]

    assert_series_equal(expected, parser.event)

    assert parser._event is not None
    assert_series_equal(expected, parser._event)


def test_event_property_caches(
    parser: SessionParser,
    event_schedule: DataFrame,
) -> None:
    event_name = "Australian Grand Prix"
    parser._event_name = event_name
    parser._event_schedule = event_schedule

    expected = event_schedule[event_schedule["EventName"] == event_name].iloc[0]

    assert_series_equal(expected, parser.event), "First time computes"
    assert_series_equal(expected, parser.event), "Second time returns cachee"


@pytest.mark.parametrize(
    ("event_name", "event", "expected"),
    [
        (None, None, ["Session"]),
        ("E1", Series({"EventFormat": "sprint"}), ["Session"] + SprintQualifyingSessionIdentifiers.all_values()),
        ("E2", Series({"EventFormat": "sprint_shootout"}), ["Session"] + SprintQualifyingSessionIdentifiers.all_values()),
        ("E3", Series({"EventFormat": "sprint_qualifying"}), ["Session"] + SprintQualifyingSessionIdentifiers.all_values()),
        ("E4", Series({"EventFormat": "conventional"}), ["Session"] + ConventionalSessionIdentifiers.all_values()),
        ("E5", Series({"EventFormat": "default"}), ["Session"] + ConventionalSessionIdentifiers.all_values()),
    ]
)
def test_session_names_property(
    event_name: str | None,
    event: Series | None,
    expected: list[str],
    parser: SessionParser
) -> None:
    parser._event_name = event_name
    parser._event = event

    assert expected == parser.session_names


def test_session_property_computes_when_none(
    parser: SessionParser,
    mock_session: MagicMock,
    mocker: MockerFixture,
) -> None:
    assert parser._session is None

    year = 2026
    event_name = "Australian Grand Prix"
    session_id = "Race"

    parser._year = year
    parser._event_name = event_name
    parser._session_id = session_id

    mock_get_session = mocker.MagicMock(return_value=mock_session)
    mocker.patch("f1p.services.data_extractor.parsers.session.fastf1.get_session", mock_get_session)

    assert mock_session == parser.session

    assert parser._session is not None
    assert mock_session == parser._session

    mock_get_session.assert_called_once_with(year, event_name, session_id)


def test_session_property_caches(
    parser: SessionParser,
    mock_session: MagicMock,
    mocker: MockerFixture,
) -> None:
    assert parser._session is None

    year = 2026
    event_name = "Australian Grand Prix"
    session_id = "Race"

    parser._year = year
    parser._event_name = event_name
    parser._session_id = session_id

    mock_get_session = mocker.MagicMock(return_value=mock_session)
    mocker.patch("f1p.services.data_extractor.parsers.session.fastf1.get_session", mock_get_session)

    assert mock_session == parser.session, "First time computes"
    assert mock_session == parser.session,  "Second time returns cachee"

    mock_get_session.assert_called_once_with(year, event_name, session_id)
