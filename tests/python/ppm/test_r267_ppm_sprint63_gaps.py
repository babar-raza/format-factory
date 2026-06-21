"""Tests for PPM Sprint 63 gap closure.

Closes:
  GAP-PPM-FOSS-PPM_IS_MULTI-001   (Ppm Is Multi Row)
  GAP-PPM-FOSS-PPM_HAS_MULT-001   (Ppm Has Multi Channel Pixels)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ppm import ppm_is_multi_row, ppm_has_multi_channel_pixels

_DIR = _REPO / "samples" / "by-format" / "ppm" / "valid"
_1X1_RED = str(_DIR / "1x1-red.ppm")
_2X2 = str(_DIR / "2x2-rgbw.ppm")
_3X1 = str(_DIR / "3x1-gradient.ppm")


class TestPpmIsMultiRow:
    def test_return_type(self):
        assert isinstance(ppm_is_multi_row(_1X1_RED), bool)

    def test_false_for_1x1(self):
        assert ppm_is_multi_row(_1X1_RED) is False

    def test_true_for_2x2(self):
        assert ppm_is_multi_row(_2X2) is True

    def test_false_for_3x1(self):
        assert ppm_is_multi_row(_3X1) is False

    def test_consistent_across_calls(self):
        assert ppm_is_multi_row(_1X1_RED) == ppm_is_multi_row(_1X1_RED)


class TestPpmHasMultiChannelPixels:
    def test_return_type(self):
        assert isinstance(ppm_has_multi_channel_pixels(_1X1_RED), bool)

    def test_false_for_1x1_red(self):
        assert ppm_has_multi_channel_pixels(_1X1_RED) is False

    def test_true_for_2x2(self):
        assert ppm_has_multi_channel_pixels(_2X2) is True

    def test_true_for_3x1_gradient(self):
        assert ppm_has_multi_channel_pixels(_3X1) is True

    def test_consistent_across_calls(self):
        assert ppm_has_multi_channel_pixels(_1X1_RED) == ppm_has_multi_channel_pixels(_1X1_RED)
