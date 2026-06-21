"""Tests for ppm_total_green_sum and ppm_avg_green_channel (Sprint r297)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ppm.ppm_parser import ppm_total_green_sum, ppm_avg_green_channel

_PPM = _REPO / "samples" / "by-format" / "ppm" / "valid"


class TestPpmTotalGreenSum:
    """Tests for ppm_total_green_sum."""

    def test_1x1_red_has_zero_green_sum(self):
        """1x1-red.ppm is fully red, so green channel sum is 0."""
        result = ppm_total_green_sum(_PPM / "1x1-red.ppm")
        assert result == 0

    def test_2x2_rgbw_green_sum_is_510(self):
        """2x2-rgbw.ppm: pixels (255,0,0),(0,255,0),(0,0,255),(255,255,255) → green=510."""
        result = ppm_total_green_sum(_PPM / "2x2-rgbw.ppm")
        assert result == 510

    def test_3x1_gradient_green_sum_is_383(self):
        """3x1-gradient.ppm: pixels (0,0,0),(128,128,128),(255,255,255) → green=383."""
        result = ppm_total_green_sum(_PPM / "3x1-gradient.ppm")
        assert result == 383

    def test_returns_int(self):
        result = ppm_total_green_sum(_PPM / "1x1-red.ppm")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for f in ["1x1-red.ppm", "2x2-rgbw.ppm", "3x1-gradient.ppm"]:
            assert ppm_total_green_sum(_PPM / f) >= 0

    def test_rgbw_has_highest_green_sum(self):
        r1 = ppm_total_green_sum(_PPM / "1x1-red.ppm")
        r2 = ppm_total_green_sum(_PPM / "2x2-rgbw.ppm")
        assert r2 > r1


class TestPpmAvgGreenChannel:
    """Tests for ppm_avg_green_channel."""

    def test_1x1_red_avg_green_is_zero(self):
        """1x1-red.ppm is fully red, so average green is 0.0."""
        result = ppm_avg_green_channel(_PPM / "1x1-red.ppm")
        assert result == 0.0

    def test_2x2_rgbw_avg_green_is_127_5(self):
        """2x2-rgbw.ppm: green sum=510, 4 pixels → avg=127.5."""
        result = ppm_avg_green_channel(_PPM / "2x2-rgbw.ppm")
        assert result == 127.5

    def test_3x1_gradient_avg_green_is_approx_127_67(self):
        """3x1-gradient.ppm: green sum=383, 3 pixels → avg≈127.67."""
        result = ppm_avg_green_channel(_PPM / "3x1-gradient.ppm")
        assert round(result, 2) == 127.67

    def test_returns_float(self):
        result = ppm_avg_green_channel(_PPM / "2x2-rgbw.ppm")
        assert isinstance(result, float)

    def test_nonnegative(self):
        for f in ["1x1-red.ppm", "2x2-rgbw.ppm", "3x1-gradient.ppm"]:
            assert ppm_avg_green_channel(_PPM / f) >= 0.0

    def test_rgbw_has_higher_avg_than_red(self):
        r1 = ppm_avg_green_channel(_PPM / "1x1-red.ppm")
        r2 = ppm_avg_green_channel(_PPM / "2x2-rgbw.ppm")
        assert r2 > r1
