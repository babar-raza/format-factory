"""Tests for QOI Sprint 61 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_BLUE_MEA-001   (Qoi Blue Mean Value)
  GAP-QOI-FOSS-QOI_DARK_RAT-001   (Qoi Dark Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_blue_mean_value, qoi_dark_ratio

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiBlueMeanValue:
    def test_return_type(self):
        assert isinstance(qoi_blue_mean_value(_RED), (int, float))

    def test_zero_for_red(self):
        assert qoi_blue_mean_value(_RED) == 0.0

    def test_zero_for_black(self):
        assert qoi_blue_mean_value(_BLACK) == 0.0

    def test_exact_127_5_for_gradient(self):
        assert qoi_blue_mean_value(_GRAD) == 127.5

    def test_nonnegative(self):
        assert qoi_blue_mean_value(_RED) >= 0

    def test_consistent_across_calls(self):
        assert qoi_blue_mean_value(_RED) == qoi_blue_mean_value(_RED)


class TestQoiDarkRatio:
    def test_return_type(self):
        assert isinstance(qoi_dark_ratio(_RED), (int, float))

    def test_zero_for_red(self):
        assert qoi_dark_ratio(_RED) == 0.0

    def test_exact_1_0_for_black(self):
        assert qoi_dark_ratio(_BLACK) == 1.0

    def test_exact_0_25_for_gradient(self):
        assert qoi_dark_ratio(_GRAD) == 0.25

    def test_between_0_and_1(self):
        assert 0.0 <= qoi_dark_ratio(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_dark_ratio(_RED) == qoi_dark_ratio(_RED)
