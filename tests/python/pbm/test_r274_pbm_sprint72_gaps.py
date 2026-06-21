"""Tests for PBM Sprint 72 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_IS_MULTI-001   (Pbm Is Multi Row)
  GAP-PBM-FOSS-PBM_PIXEL_SU-001   (Pbm Pixel Sum)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_is_multi_row, pbm_pixel_sum

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmIsMultiRow:
    def test_return_type(self):
        assert isinstance(pbm_is_multi_row(_BLACK), bool)

    def test_false_for_1x1_black(self):
        assert pbm_is_multi_row(_BLACK) is False

    def test_true_for_2x2_checker(self):
        assert pbm_is_multi_row(_CHECKER) is True

    def test_true_for_3x2_pattern(self):
        assert pbm_is_multi_row(_PATTERN) is True

    def test_is_boolean(self):
        assert pbm_is_multi_row(_BLACK) in (True, False)

    def test_consistent_across_calls(self):
        assert pbm_is_multi_row(_BLACK) == pbm_is_multi_row(_BLACK)


class TestPbmPixelSum:
    def test_return_type(self):
        assert isinstance(pbm_pixel_sum(_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_pixel_sum(_BLACK) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_pixel_sum(_CHECKER) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_pixel_sum(_PATTERN) == 3

    def test_positive(self):
        assert pbm_pixel_sum(_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_pixel_sum(_BLACK) == pbm_pixel_sum(_BLACK)
