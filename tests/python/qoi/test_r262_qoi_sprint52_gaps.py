"""Tests for QOI Sprint 52 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_IS_SINGL-001  (Qoi Is Single Pixel)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_is_single_pixel

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRADIENT = str(_DIR / "4x1-gradient.qoi")


class TestQoiIsSinglePixel:
    def test_return_type(self):
        assert isinstance(qoi_is_single_pixel(_RED), bool)

    def test_true_for_1x1(self):
        assert qoi_is_single_pixel(_RED) is True

    def test_false_for_2x2(self):
        assert qoi_is_single_pixel(_BLACK) is False

    def test_false_for_4x1(self):
        assert qoi_is_single_pixel(_GRADIENT) is False

    def test_consistent_across_calls(self):
        assert qoi_is_single_pixel(_RED) == qoi_is_single_pixel(_RED)
