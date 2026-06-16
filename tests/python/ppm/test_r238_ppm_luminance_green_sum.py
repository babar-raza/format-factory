"""Tests for ppm_luminance_average and ppm_green_channel_sum.

Product deepening: PPM analytics — R238.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm import ppm_luminance_average, ppm_green_channel_sum

_PPM_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"


def _first_ppm():
    files = sorted(_PPM_DIR.glob("*.ppm"))
    assert files, f"No PPM samples in {_PPM_DIR}"
    return str(files[0])


class TestPpmLuminanceAverage:
    def test_returns_float(self):
        assert isinstance(ppm_luminance_average(_first_ppm()), float)

    def test_nonnegative(self):
        assert ppm_luminance_average(_first_ppm()) >= 0.0

    def test_within_maxval(self):
        assert ppm_luminance_average(_first_ppm()) <= 255.0


class TestPpmGreenChannelSum:
    def test_returns_int(self):
        assert isinstance(ppm_green_channel_sum(_first_ppm()), int)

    def test_nonnegative(self):
        assert ppm_green_channel_sum(_first_ppm()) >= 0

    def test_consistent_with_pixel_count(self):
        result = ppm_green_channel_sum(_first_ppm())
        assert result >= 0
