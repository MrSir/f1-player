import pytest

from f1p.utils.color import hex_to_rgb_saturation


@pytest.mark.parametrize(
    ("hex", "expected"),
    [
        ("ffffff", {"hex": f"#ffffff", "rgb": (255, 255, 255), "saturation_hls": 1.0}),
        ("000000", {"hex": f"#000000", "rgb": (0, 0, 0), "saturation_hls": 1.0}),
        ("ff0000", {"hex": f"#ff0000", "rgb": (255, 0, 0), "saturation_hls": 1.0}),
        ("00ff00", {"hex": f"#00ff00", "rgb": (0, 255, 0), "saturation_hls": 1.0}),
        ("0000ff", {"hex": f"#0000ff", "rgb": (0, 0, 255), "saturation_hls": 1.0}),
    ],
)
def test_hex_to_rgb_saturation(hex: str, expected: dict) -> None:
    assert expected == hex_to_rgb_saturation(hex)
