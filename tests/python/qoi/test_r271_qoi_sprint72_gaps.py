"""Tests for QOI Sprint 72 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_ALPHA_RA-001   (Qoi Alpha Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_alpha_ratio

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiAlphaRatio:
    def test_return_type(self):
        assert isinstance(qoi_alpha_ratio(_RED), (int, float))

    def test_exact_1_0_for_1x1_red(self):
        assert qoi_alpha_ratio(_RED) == 1.0

    def test_zero_for_2x2_black(self):
        assert qoi_alpha_ratio(_BLACK) == 0.0

    def test_exact_1_0_for_gradient(self):
        assert qoi_alpha_ratio(_GRAD) == 1.0

    def test_between_0_and_1(self):
        assert 0.0 <= qoi_alpha_ratio(_RED) <= 1.0

    def test_consistent_across_calls(self):
        assert qoi_alpha_ratio(_RED) == qoi_alpha_ratio(_RED)
