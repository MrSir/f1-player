from enum import Enum

import pytest

from f1p.services.data_extractor.enums import SprintQualifyingSessionIdentifiers


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Practice 1", SprintQualifyingSessionIdentifiers.FREE_PRACTICE_1),
        ("Sprint Qualifying", SprintQualifyingSessionIdentifiers.SPRINT_QUALIFYING),
        ("Sprint", SprintQualifyingSessionIdentifiers.SPRINT),
        ("Qualifying", SprintQualifyingSessionIdentifiers.QUALIFYING),
        ("Race", SprintQualifyingSessionIdentifiers.RACE),
    ],
)
def test_initialization(value: str, expected: SprintQualifyingSessionIdentifiers) -> None:
    enum = SprintQualifyingSessionIdentifiers(value)

    assert isinstance(enum, Enum)
    assert enum == expected


def test_all_values() -> None:
    assert [
        "Practice 1",
        "Sprint Qualifying",
        "Sprint",
        "Qualifying",
        "Race",
    ] == SprintQualifyingSessionIdentifiers.all_values()
