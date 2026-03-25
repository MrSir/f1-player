from enum import Enum

import pytest

from f1p.services.data_extractor.enums import ConventionalSessionIdentifiers


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("Race", ConventionalSessionIdentifiers.RACE),
    ],
)
def test_initialization(value: str, expected: ConventionalSessionIdentifiers) -> None:
    enum = ConventionalSessionIdentifiers(value)

    assert isinstance(enum, Enum)
    assert enum == expected


def test_all_values() -> None:
    assert [
        "Race",
    ] == ConventionalSessionIdentifiers.all_values()
