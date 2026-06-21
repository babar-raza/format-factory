"""Tests for qoi_avg_rgb_value (Sprint 40 batch 2).

Closes:
  GAP-QOI-FOSS-QOI_AVG_CHAN-001  (Qoi Avg Channel Value)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_avg_rgb_value

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_1X1_RED = str(_DIR / "1x1-red.qoi")
_2X2_BLACK = str(_DIR / "2x2-black.qoi")
_4X1_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiAvgRgbValue:
    def test_return_type(self):
        assert isinstance(qoi_avg_rgb_value(_1X1_RED), float)

    def test_exact_85_0_for_1x1_red(self):
        # R=255, G=0, B=0 -> avg = (255+0+0)/3 = 85.0
        assert qoi_avg_rgb_value(_1X1_RED) == 85.0

    def test_zero_for_2x2_black(self):
        assert qoi_avg_rgb_value(_2X2_BLACK) == 0.0

    def test_exact_127_5_for_gradient(self):
        assert qoi_avg_rgb_value(_4X1_GRAD) == 127.5

    def test_nonnegative(self):
        assert qoi_avg_rgb_value(_1X1_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_avg_rgb_value(_1X1_RED) == qoi_avg_rgb_value(_1X1_RED)
