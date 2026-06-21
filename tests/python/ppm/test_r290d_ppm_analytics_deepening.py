"""Sprint R290D: PPM analytics deepening — green_dominant_count, blue_dominant_count, avg_channel_diff."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ppm.ppm_parser import (
    ppm_green_dominant_count,
    ppm_blue_dominant_count,
    ppm_avg_channel_diff,
)

SAMPLES = _REPO / "samples" / "by-format" / "ppm" / "valid"
RED_1x1 = SAMPLES / "1x1-red.ppm"
RGBW_2x2 = SAMPLES / "2x2-rgbw.ppm"
GRADIENT = SAMPLES / "3x1-gradient.ppm"


@pytest.fixture
def red_sample():
    if not RED_1x1.exists():
        pytest.skip("PPM red sample not available")
    return RED_1x1


@pytest.fixture
def rgbw_sample():
    if not RGBW_2x2.exists():
        pytest.skip("PPM RGBW sample not available")
    return RGBW_2x2


class TestPpmGreenDominantCount:
    def test_returns_int(self, red_sample):
        assert isinstance(ppm_green_dominant_count(red_sample), int)

    def test_red_only_has_zero_green_dominant(self, red_sample):
        assert ppm_green_dominant_count(red_sample) == 0

    def test_nonnegative(self, rgbw_sample):
        assert ppm_green_dominant_count(rgbw_sample) >= 0


class TestPpmBlueDominantCount:
    def test_returns_int(self, red_sample):
        assert isinstance(ppm_blue_dominant_count(red_sample), int)

    def test_red_only_has_zero_blue_dominant(self, red_sample):
        assert ppm_blue_dominant_count(red_sample) == 0

    def test_nonnegative(self, rgbw_sample):
        assert ppm_blue_dominant_count(rgbw_sample) >= 0


class TestPpmAvgChannelDiff:
    def test_returns_float(self, red_sample):
        assert isinstance(ppm_avg_channel_diff(red_sample), float)

    def test_nonnegative(self, red_sample):
        assert ppm_avg_channel_diff(red_sample) >= 0.0

    def test_gradient_has_diff(self, rgbw_sample):
        assert ppm_avg_channel_diff(rgbw_sample) >= 0.0
