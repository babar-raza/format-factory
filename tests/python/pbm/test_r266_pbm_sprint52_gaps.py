"""Tests for PBM Sprint 52 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_BORDER_P-001  (Pbm Border Pixel Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_border_pixel_count

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmBorderPixelCount:
    def test_return_type(self):
        assert isinstance(pbm_border_pixel_count(_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_border_pixel_count(_BLACK) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_border_pixel_count(_CHECKER) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_border_pixel_count(_PATTERN) == 3

    def test_positive(self):
        assert pbm_border_pixel_count(_BLACK) > 0

    def test_consistent_across_calls(self):
        assert pbm_border_pixel_count(_BLACK) == pbm_border_pixel_count(_BLACK)
