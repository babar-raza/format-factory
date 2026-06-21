"""Tests for QOI Sprint 76 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_RED_MEAN-001   (Qoi Red Mean Value)
"""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_red_mean_value

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiRedMeanValue:
    def test_return_type(self):
        assert isinstance(qoi_red_mean_value(_RED), (int, float))

    def test_exact_255_for_1x1_red(self):
        assert qoi_red_mean_value(_RED) == pytest.approx(255.0)

    def test_exact_0_for_black(self):
        assert qoi_red_mean_value(_BLACK) == pytest.approx(0.0)

    def test_exact_127_5_for_gradient(self):
        assert qoi_red_mean_value(_GRAD) == pytest.approx(127.5)

    def test_nonnegative(self):
        assert qoi_red_mean_value(_RED) >= 0.0

    def test_consistent_across_calls(self):
        assert qoi_red_mean_value(_RED) == qoi_red_mean_value(_RED)
