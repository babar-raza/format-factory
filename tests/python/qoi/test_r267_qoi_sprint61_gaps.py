"""Tests for QOI Sprint 61 gap closure (batch 2).

Closes:
  GAP-QOI-FOSS-QOI_AVG_RGB_-001   (Qoi Avg Rgb Per Pixel)
  GAP-QOI-FOSS-QOI_IS_MULTI-001   (Qoi Is Multi Row)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_avg_rgb_per_pixel, qoi_is_multi_row

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiAvgRgbPerPixel:
    def test_return_type(self):
        assert isinstance(qoi_avg_rgb_per_pixel(_RED), (int, float))

    def test_exact_255_for_red(self):
        assert qoi_avg_rgb_per_pixel(_RED) == 255.0

    def test_exact_0_for_black(self):
        assert qoi_avg_rgb_per_pixel(_BLACK) == 0.0

    def test_exact_382_5_for_gradient(self):
        assert qoi_avg_rgb_per_pixel(_GRAD) == 382.5

    def test_nonnegative(self):
        assert qoi_avg_rgb_per_pixel(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_avg_rgb_per_pixel(_RED) == qoi_avg_rgb_per_pixel(_RED)


class TestQoiIsMultiRow:
    def test_return_type(self):
        assert isinstance(qoi_is_multi_row(_RED), bool)

    def test_false_for_1x1_red(self):
        assert qoi_is_multi_row(_RED) is False

    def test_true_for_2x2_black(self):
        assert qoi_is_multi_row(_BLACK) is True

    def test_false_for_4x1_gradient(self):
        assert qoi_is_multi_row(_GRAD) is False

    def test_consistent_across_calls(self):
        assert qoi_is_multi_row(_RED) == qoi_is_multi_row(_RED)
