"""Tests for QOI Sprint 41 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_WARM_PIX-001  (Qoi Warm Pixel Count)
  GAP-QOI-FOSS-QOI_COLD_PIX-001  (Qoi Cold Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_cold_pixel_count, qoi_warm_pixel_count

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")
_2X2_BLACK = str(_DIR / "2x2-black.qoi")
_4X1_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiWarmPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_warm_pixel_count(_1X1_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert qoi_warm_pixel_count(_1X1_RED) == 1

    def test_zero_for_2x2_black(self):
        assert qoi_warm_pixel_count(_2X2_BLACK) == 0

    def test_nonnegative(self):
        assert qoi_warm_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_warm_pixel_count(_1X1_RED) == qoi_warm_pixel_count(_1X1_RED)


class TestQoiColdPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_cold_pixel_count(_1X1_RED), int)

    def test_zero_for_1x1_red(self):
        assert qoi_cold_pixel_count(_1X1_RED) == 0

    def test_zero_for_2x2_black(self):
        assert qoi_cold_pixel_count(_2X2_BLACK) == 0

    def test_nonnegative(self):
        assert qoi_cold_pixel_count(_1X1_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_cold_pixel_count(_1X1_RED) == qoi_cold_pixel_count(_1X1_RED)
