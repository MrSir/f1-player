from enum import Enum

import pytest

from f1p.services.data_extractor.enums import SprintQualifyingSessionIdentifiers


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Sprint", SprintQualifyingSessionIdentifiers.SPRINT),
        ("Race", SprintQualifyingSessionIdentifiers.RACE),
    ],
)
def test_initialization(value: str, expected: SprintQualifyingSessionIdentifiers) -> None:
    enum = SprintQualifyingSessionIdentifiers(value)

    assert isinstance(enum, Enum)
    assert enum == expected


def test_all_values() -> None:
    assert [
        "Sprint",
        "Race",
    ] == SprintQualifyingSessionIdentifiers.all_values()
