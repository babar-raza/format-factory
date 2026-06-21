"""Tests for PPM Sprint 50 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_TOTAL_GR-001  (Ppm Total Green Sum)
  GAP-PPM-FOSS-PPM_AVG_GREE-001  (Ppm Avg Green Channel)
  GAP-PPM-FOSS-PPM_GREEN_DO-001  (Ppm Green Dominant Count)
  GAP-PPM-FOSS-PPM_BLUE_DOM-001  (Ppm Blue Dominant Count)
  GAP-PPM-FOSS-PPM_AVG_CHAN-001  (Ppm Avg Channel Diff)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import (
    ppm_total_green_sum,
    ppm_avg_green_channel,
    ppm_green_dominant_count,
    ppm_blue_dominant_count,
    ppm_avg_channel_diff,
)

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_RED = str(_DIR / "1x1-red.ppm")
_RGBW = str(_DIR / "2x2-rgbw.ppm")


class TestPpmTotalGreenSum:
    def test_return_type(self):
        assert isinstance(ppm_total_green_sum(_RED), (int, float))

    def test_zero_for_red(self):
        assert ppm_total_green_sum(_RED) == 0

    def test_exact_510_for_rgbw(self):
        assert ppm_total_green_sum(_RGBW) == 510

    def test_nonnegative(self):
        assert ppm_total_green_sum(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_total_green_sum(_RED) == ppm_total_green_sum(_RED)


class TestPpmAvgGreenChannel:
    def test_return_type(self):
        assert isinstance(ppm_avg_green_channel(_RED), (int, float))

    def test_zero_for_red(self):
        assert ppm_avg_green_channel(_RED) == 0.0

    def test_exact_127_5_for_rgbw(self):
        assert ppm_avg_green_channel(_RGBW) == 127.5

    def test_nonnegative(self):
        assert ppm_avg_green_channel(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_avg_green_channel(_RED) == ppm_avg_green_channel(_RED)


class TestPpmGreenDominantCount:
    def test_return_type(self):
        assert isinstance(ppm_green_dominant_count(_RED), int)

    def test_zero_for_red(self):
        assert ppm_green_dominant_count(_RED) == 0

    def test_exact_1_for_rgbw(self):
        assert ppm_green_dominant_count(_RGBW) == 1

    def test_nonnegative(self):
        assert ppm_green_dominant_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_green_dominant_count(_RED) == ppm_green_dominant_count(_RED)


class TestPpmBlueDominantCount:
    def test_return_type(self):
        assert isinstance(ppm_blue_dominant_count(_RED), int)

    def test_zero_for_red(self):
        assert ppm_blue_dominant_count(_RED) == 0

    def test_exact_1_for_rgbw(self):
        assert ppm_blue_dominant_count(_RGBW) == 1

    def test_nonnegative(self):
        assert ppm_blue_dominant_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_blue_dominant_count(_RED) == ppm_blue_dominant_count(_RED)


class TestPpmAvgChannelDiff:
    def test_return_type(self):
        assert isinstance(ppm_avg_channel_diff(_RED), (int, float))

    def test_exact_255_for_red(self):
        assert ppm_avg_channel_diff(_RED) == 255.0

    def test_exact_191_25_for_rgbw(self):
        assert ppm_avg_channel_diff(_RGBW) == 191.25

    def test_nonnegative(self):
        assert ppm_avg_channel_diff(_RED) >= 0

    def test_consistent_across_calls(self):
        assert ppm_avg_channel_diff(_RED) == ppm_avg_channel_diff(_RED)
