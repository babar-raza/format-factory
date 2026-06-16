"""Tests for qoi_row_count and qoi_is_square (Sprint 34)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.qoi import qoi_row_count, qoi_is_square

_QOI_DIR = _REPO / "samples" / "by-format" / "qoi" / "valid"

# 1x1-red.qoi is square (1x1); 4x1-gradient.qoi is not square (4x1)
_SQUARE = str(_QOI_DIR / "1x1-red.qoi")
_NONSQUARE = str(_QOI_DIR / "4x1-gradient.qoi")
_2X2 = str(_QOI_DIR / "2x2-black.qoi")


class TestQoiRowCount:
    def test_return_type(self):
        result = qoi_row_count(_SQUARE)
        assert isinstance(result, int)

    def test_one_row_for_1x1(self):
        assert qoi_row_count(_SQUARE) == 1

    def test_one_row_for_4x1(self):
        assert qoi_row_count(_NONSQUARE) == 1

    def test_two_rows_for_2x2(self):
        assert qoi_row_count(_2X2) == 2

    def test_nonnegative(self):
        assert qoi_row_count(_SQUARE) >= 0


class TestQoiIsSquare:
    def test_return_type(self):
        result = qoi_is_square(_SQUARE)
        assert isinstance(result, bool)

    def test_true_for_1x1(self):
        assert qoi_is_square(_SQUARE) is True

    def test_true_for_2x2(self):
        assert qoi_is_square(_2X2) is True

    def test_false_for_4x1(self):
        assert qoi_is_square(_NONSQUARE) is False

    def test_consistent_across_calls(self):
        assert qoi_is_square(_SQUARE) == qoi_is_square(_SQUARE)
