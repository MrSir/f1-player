from enum import Enum

import pytest

from f1p.services.data_extractor.enums import ConventionalSessionIdentifiers


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Practice 1", ConventionalSessionIdentifiers.FREE_PRACTICE_1),
        ("Practice 2", ConventionalSessionIdentifiers.FREE_PRACTICE_2),
        ("Practice 3", ConventionalSessionIdentifiers.FREE_PRACTICE_3),
        ("Qualifying", ConventionalSessionIdentifiers.QUALIFYING),
        ("Race", ConventionalSessionIdentifiers.RACE),
    ],
)
def test_initialization(value: str, expected: ConventionalSessionIdentifiers) -> None:
    enum = ConventionalSessionIdentifiers(value)

    assert isinstance(enum, Enum)
    assert enum == expected
