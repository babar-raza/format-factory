"""Tests for QOI Sprint 57 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_BLACK_PI-001   (Qoi Black Pixel Count)
  GAP-QOI-FOSS-QOI_WHITE_PI-001   (Qoi White Pixel Count)
  GAP-QOI-FOSS-QOI_AVG_SATU-001   (Qoi Avg Saturation)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_black_pixel_count, qoi_white_pixel_count, qoi_avg_saturation

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiBlackPixelCount:
    def test_return_type(self):
        assert isinstance(qoi_black_pixel_count(_RED), int)

    def test_zero_for_red(self):
        assert qoi_black_pixel_count(_RED) == 0

    def test_exact_4_for_black(self):
        assert qoi_black_pixel_count(_BLACK) == 4

    def test_exact_1_for_gradient(self):
        assert qoi_black_pixel_count(_GRAD) == 1

    def test_nonnegative(self):
        assert qoi_black_pixel_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_black_pixel_count(_RED) == qoi_black_pixel_count(_RED)


class TestQoiWhitePixelCount:
    def test_return_type(self):
        assert isinstance(qoi_white_pixel_count(_RED), int)

    def test_zero_for_red(self):
        assert qoi_white_pixel_count(_RED) == 0

    def test_zero_for_black(self):
        assert qoi_white_pixel_count(_BLACK) == 0

    def test_exact_1_for_gradient(self):
        assert qoi_white_pixel_count(_GRAD) == 1

    def test_nonnegative(self):
        assert qoi_white_pixel_count(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_white_pixel_count(_RED) == qoi_white_pixel_count(_RED)


class TestQoiAvgSaturation:
    def test_return_type(self):
        assert isinstance(qoi_avg_saturation(_RED), (int, float))

    def test_exact_1_0_for_red(self):
        assert qoi_avg_saturation(_RED) == 1.0

    def test_exact_0_0_for_black(self):
        assert qoi_avg_saturation(_BLACK) == 0.0

    def test_exact_0_0_for_gradient(self):
        assert qoi_avg_saturation(_GRAD) == 0.0

    def test_between_0_and_1(self):
        assert 0.0 <= qoi_avg_saturation(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_avg_saturation(_RED) == qoi_avg_saturation(_RED)
