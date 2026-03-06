from enum import Enum

import pytest

from f1p.ui.components.camera.enums import CameraType


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("ORBITING", CameraType.ORBITING),
        ("TOP_DOWN", CameraType.TOP_DOWN),
    ],
)
def test_initialization(value: str, expected: CameraType) -> None:
    enum = CameraType(value)

    assert isinstance(enum, Enum)
    assert enum == expected
