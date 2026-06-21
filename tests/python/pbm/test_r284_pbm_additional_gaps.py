"""
Tests for additional PBM analytics gap closure (6 FOSS gaps).
Closes: PBM_ROW_DENS, PBM_IS_CHECK, PBM_COLUMN_D,
        PBM_IS_ALL_B, PBM_TOTAL_BL, PBM_CENTER_B
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm.pbm_parser import (
    pbm_row_density_variance,
    pbm_is_checkerboard,
    pbm_column_density_variance,
    pbm_is_all_black,
    pbm_total_black_in_border,
    pbm_center_black_ratio,
)

_PBM_BLACK = _REPO / "samples/by-format/pbm/valid/1x1-black.pbm"
_PBM_CHECKER = _REPO / "samples/by-format/pbm/valid/2x2-checker.pbm"
_PBM_PATTERN = _REPO / "samples/by-format/pbm/valid/3x2-pattern.pbm"


class TestPbmRowDensityVariance:
    def test_returns_float(self):
        assert isinstance(pbm_row_density_variance(_PBM_BLACK), float)

    def test_nonnegative(self):
        assert pbm_row_density_variance(_PBM_BLACK) >= 0.0

    def test_1x1_zero_variance(self):
        # 1x1 has only 1 row → variance of 1 value = 0
        assert pbm_row_density_variance(_PBM_BLACK) == pytest.approx(0.0)

    def test_pattern_nonnegative(self):
        assert pbm_row_density_variance(_PBM_PATTERN) >= 0.0


class TestPbmIsCheckerboard:
    def test_returns_bool(self):
        assert isinstance(pbm_is_checkerboard(_PBM_BLACK), bool)

    def test_1x1_not_checkerboard(self):
        assert pbm_is_checkerboard(_PBM_BLACK) is False

    def test_returns_bool_for_checker(self):
        assert isinstance(pbm_is_checkerboard(_PBM_CHECKER), bool)

    def test_pattern_is_bool(self):
        assert isinstance(pbm_is_checkerboard(_PBM_PATTERN), bool)


class TestPbmColumnDensityVariance:
    def test_returns_float(self):
        assert isinstance(pbm_column_density_variance(_PBM_BLACK), float)

    def test_nonnegative(self):
        assert pbm_column_density_variance(_PBM_BLACK) >= 0.0

    def test_1x1_zero_variance(self):
        assert pbm_column_density_variance(_PBM_BLACK) == pytest.approx(0.0)

    def test_pattern_nonnegative(self):
        assert pbm_column_density_variance(_PBM_PATTERN) >= 0.0


class TestPbmIsAllBlack:
    def test_returns_bool(self):
        assert isinstance(pbm_is_all_black(_PBM_BLACK), bool)

    def test_1x1_black_is_all_black(self):
        assert pbm_is_all_black(_PBM_BLACK) is True

    def test_checker_not_all_black(self):
        assert pbm_is_all_black(_PBM_CHECKER) is False

    def test_pattern_not_all_black(self):
        assert pbm_is_all_black(_PBM_PATTERN) is False


class TestPbmTotalBlackInBorder:
    def test_returns_int(self):
        assert isinstance(pbm_total_black_in_border(_PBM_BLACK), int)

    def test_nonnegative(self):
        assert pbm_total_black_in_border(_PBM_BLACK) >= 0

    def test_1x1_black_border_count_one(self):
        assert pbm_total_black_in_border(_PBM_BLACK) == 1

    def test_checker_border_count(self):
        assert pbm_total_black_in_border(_PBM_CHECKER) == 2


class TestPbmCenterBlackRatio:
    def test_returns_float(self):
        assert isinstance(pbm_center_black_ratio(_PBM_BLACK), float)

    def test_bounded(self):
        assert 0.0 <= pbm_center_black_ratio(_PBM_BLACK) <= 1.0

    def test_1x1_no_center(self):
        # 1x1 pixel: border is the whole image; center is empty → 0.0
        assert pbm_center_black_ratio(_PBM_BLACK) == pytest.approx(0.0)

    def test_pattern_nonnegative(self):
        assert pbm_center_black_ratio(_PBM_PATTERN) >= 0.0
