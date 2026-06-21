"""Tests for QOI Sprint 70 gap closure.

Closes:
  GAP-QOI-FOSS-QOI_HEIGHT-001   (Qoi Height)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_height

_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"
_RED = str(_DIR / "1x1-red.qoi")
_BLACK = str(_DIR / "2x2-black.qoi")
_GRAD = str(_DIR / "4x1-gradient.qoi")


class TestQoiHeight:
    def test_return_type(self):
        assert isinstance(qoi_height(_RED), int)

    def test_exact_1_for_1x1_red(self):
        assert qoi_height(_RED) == 1

    def test_exact_2_for_2x2_black(self):
        assert qoi_height(_BLACK) == 2

    def test_exact_1_for_4x1_gradient(self):
        assert qoi_height(_GRAD) == 1

    def test_positive(self):
        assert qoi_height(_RED) > 0

    def test_consistent_across_calls(self):
        assert qoi_height(_RED) == qoi_height(_RED)
