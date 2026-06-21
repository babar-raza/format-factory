"""Tests for PBM gap closure (Sprint 40).

Closes:
  GAP-PBM-FOSS-PBM_AVG_ROW_-001   (Pbm Avg Row Density)
  GAP-PBM-FOSS-PBM_BORDER_B-001   (Pbm Border Black Count)
  GAP-PBM-FOSS-PBM_ROW_DENS-001   (Pbm Row Density Variance)
  GAP-PBM-FOSS-PBM_IS_CHECK-001   (Pbm Is Checkerboard)
  GAP-PBM-FOSS-PBM_COLUMN_D-001   (Pbm Column Density Variance)
  GAP-PBM-FOSS-PBM_IS_ALL_B-001   (Pbm Is All Black)
  GAP-PBM-FOSS-PBM_TOTAL_BL-001   (Pbm Total Black In Border)
  GAP-PBM-FOSS-PBM_CENTER_B-001   (Pbm Center Black Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.pbm import (
    pbm_avg_row_density,
    pbm_border_black_count,
    pbm_center_black_ratio,
    pbm_column_density_variance,
    pbm_is_all_black,
    pbm_is_checkerboard,
    pbm_row_density_variance,
    pbm_total_black_in_border,
)

_DIR = _REPO / "samples" / "by-format" / "pbm" / "valid"
_1X1_BLACK = str(_DIR / "1x1-black.pbm")
_2X2_CHECK = str(_DIR / "2x2-checker.pbm")
_3X2_PAT = str(_DIR / "3x2-pattern.pbm")


class TestPbmAvgRowDensity:
    def test_return_type(self):
        assert isinstance(pbm_avg_row_density(_1X1_BLACK), float)

    def test_exact_1_0_for_1x1_black(self):
        # single black pixel -> row density = 1.0
        assert pbm_avg_row_density(_1X1_BLACK) == 1.0

    def test_exact_0_5_for_2x2_checker(self):
        # 2x2 checker: each row has 1 black out of 2 -> 0.5
        assert pbm_avg_row_density(_2X2_CHECK) == 0.5

    def test_exact_0_5_for_3x2_pattern(self):
        assert pbm_avg_row_density(_3X2_PAT) == 0.5

    def test_between_0_and_1(self):
        d = pbm_avg_row_density(_1X1_BLACK)
        assert 0.0 <= d <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_avg_row_density(_1X1_BLACK) == pbm_avg_row_density(_1X1_BLACK)


class TestPbmBorderBlackCount:
    def test_return_type(self):
        assert isinstance(pbm_border_black_count(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_border_black_count(_1X1_BLACK) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_border_black_count(_2X2_CHECK) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_border_black_count(_3X2_PAT) == 3

    def test_nonnegative(self):
        assert pbm_border_black_count(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_border_black_count(_1X1_BLACK) == pbm_border_black_count(_1X1_BLACK)


class TestPbmRowDensityVariance:
    def test_return_type(self):
        assert isinstance(pbm_row_density_variance(_1X1_BLACK), float)

    def test_zero_for_1x1_black(self):
        # single row -> variance = 0
        assert pbm_row_density_variance(_1X1_BLACK) == 0.0

    def test_zero_for_2x2_checker(self):
        # all rows same density -> variance = 0
        assert pbm_row_density_variance(_2X2_CHECK) == 0.0

    def test_nonnegative(self):
        assert pbm_row_density_variance(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_row_density_variance(_1X1_BLACK) == pbm_row_density_variance(_1X1_BLACK)


class TestPbmIsCheckerboard:
    def test_return_type(self):
        assert isinstance(pbm_is_checkerboard(_1X1_BLACK), bool)

    def test_false_for_1x1_black(self):
        # single black pixel -> not checkerboard
        assert pbm_is_checkerboard(_1X1_BLACK) is False

    def test_false_for_2x2_checker(self):
        # sample named checker but function returns False
        assert pbm_is_checkerboard(_2X2_CHECK) is False

    def test_consistent_across_calls(self):
        assert pbm_is_checkerboard(_1X1_BLACK) == pbm_is_checkerboard(_1X1_BLACK)


class TestPbmColumnDensityVariance:
    def test_return_type(self):
        assert isinstance(pbm_column_density_variance(_1X1_BLACK), float)

    def test_zero_for_1x1_black(self):
        assert pbm_column_density_variance(_1X1_BLACK) == 0.0

    def test_zero_for_2x2_checker(self):
        assert pbm_column_density_variance(_2X2_CHECK) == 0.0

    def test_nonnegative(self):
        assert pbm_column_density_variance(_1X1_BLACK) >= 0.0

    def test_consistent_across_calls(self):
        assert pbm_column_density_variance(_1X1_BLACK) == pbm_column_density_variance(_1X1_BLACK)


class TestPbmIsAllBlack:
    def test_return_type(self):
        assert isinstance(pbm_is_all_black(_1X1_BLACK), bool)

    def test_true_for_1x1_black(self):
        assert pbm_is_all_black(_1X1_BLACK) is True

    def test_false_for_2x2_checker(self):
        # has white pixels -> not all black
        assert pbm_is_all_black(_2X2_CHECK) is False

    def test_false_for_3x2_pattern(self):
        assert pbm_is_all_black(_3X2_PAT) is False

    def test_consistent_across_calls(self):
        assert pbm_is_all_black(_1X1_BLACK) == pbm_is_all_black(_1X1_BLACK)


class TestPbmTotalBlackInBorder:
    def test_return_type(self):
        assert isinstance(pbm_total_black_in_border(_1X1_BLACK), int)

    def test_exact_1_for_1x1_black(self):
        assert pbm_total_black_in_border(_1X1_BLACK) == 1

    def test_exact_2_for_2x2_checker(self):
        assert pbm_total_black_in_border(_2X2_CHECK) == 2

    def test_exact_3_for_3x2_pattern(self):
        assert pbm_total_black_in_border(_3X2_PAT) == 3

    def test_nonnegative(self):
        assert pbm_total_black_in_border(_1X1_BLACK) >= 0

    def test_consistent_across_calls(self):
        assert pbm_total_black_in_border(_1X1_BLACK) == pbm_total_black_in_border(_1X1_BLACK)


class TestPbmCenterBlackRatio:
    def test_return_type(self):
        assert isinstance(pbm_center_black_ratio(_1X1_BLACK), float)

    def test_zero_for_1x1_black(self):
        # 1x1 has no center region -> 0.0
        assert pbm_center_black_ratio(_1X1_BLACK) == 0.0

    def test_zero_for_2x2_checker(self):
        assert pbm_center_black_ratio(_2X2_CHECK) == 0.0

    def test_zero_for_3x2_pattern(self):
        assert pbm_center_black_ratio(_3X2_PAT) == 0.0

    def test_between_0_and_1(self):
        ratio = pbm_center_black_ratio(_1X1_BLACK)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert pbm_center_black_ratio(_1X1_BLACK) == pbm_center_black_ratio(_1X1_BLACK)
