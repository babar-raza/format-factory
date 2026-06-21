"""Tests for PBM Sprint 68 gap closure.

Closes:
  GAP-PBM-FOSS-PBM_ROW_WHIT-001   (Pbm Row White Ratio)
  GAP-PBM-FOSS-PBM_CENTER_R-001   (Pbm Center Region Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import pbm_row_white_ratio, pbm_center_region_density

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_BLACK = str(_DIR / "1x1-black.pbm")
_CHECKER = str(_DIR / "2x2-checker.pbm")
_PATTERN = str(_DIR / "3x2-pattern.pbm")


class TestPbmRowWhiteRatio:
    def test_return_type(self):
        assert isinstance(pbm_row_white_ratio(_BLACK), (int, float))

    def test_zero_for_all_black(self):
        assert pbm_row_white_ratio(_BLACK) == 0.0

    def test_exact_0_5_for_checker(self):
        assert pbm_row_white_ratio(_CHECKER) == 0.5

    def test_exact_0_5_for_pattern(self):
        assert pbm_row_white_ratio(_PATTERN) == 0.5

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_row_white_ratio(_CHECKER) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_row_white_ratio(_BLACK) == pbm_row_white_ratio(_BLACK)


class TestPbmCenterRegionDensity:
    def test_return_type(self):
        assert isinstance(pbm_center_region_density(_BLACK), (int, float))

    def test_zero_for_all_black(self):
        assert pbm_center_region_density(_BLACK) == 0.0

    def test_exact_1_0_for_checker(self):
        assert pbm_center_region_density(_CHECKER) == 1.0

    def test_exact_0_5_for_pattern(self):
        assert pbm_center_region_density(_PATTERN) == 0.5

    def test_between_0_and_1(self):
        assert 0.0 <= pbm_center_region_density(_CHECKER) <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_center_region_density(_BLACK) == pbm_center_region_density(_BLACK)
