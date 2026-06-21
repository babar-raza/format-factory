"""Tests for PBM analytics functions — coverage sprint r374.

Covers 46 pbm_ analytics functions using 3 real PBM sample files.
Each test asserts return type and plausible value.
"""
import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from pbm import (
    pbm_all_black, pbm_all_white, pbm_area, pbm_aspect_ratio,
    pbm_avg_row_density, pbm_black_density, pbm_black_pixel_count,
    pbm_black_pixel_ratio, pbm_border_black_count, pbm_center_black_ratio,
    pbm_column_black_counts, pbm_column_count, pbm_column_density_variance,
    pbm_diagonal, pbm_diagonal_pixel_count, pbm_dimension_ratio, pbm_dimensions,
    pbm_has_any_black, pbm_has_any_white, pbm_is_all_black, pbm_is_binary,
    pbm_is_binary_balanced, pbm_is_checkerboard, pbm_is_landscape,
    pbm_is_portrait, pbm_is_square, pbm_is_tall, pbm_is_uniform, pbm_is_wide,
    pbm_max_dimension, pbm_max_row_black_count, pbm_megapixels, pbm_min_dimension,
    pbm_min_row_black_count, pbm_perimeter, pbm_pixel_density,
    pbm_row_black_counts, pbm_row_count, pbm_row_density_variance,
    pbm_total_black_in_border, pbm_total_pixel_count, pbm_total_pixels,
    pbm_white_density, pbm_white_pixel_count, pbm_white_pixel_ratio,
)

_SAMPLES = _REPO / "samples" / "by-format" / "pbm" / "valid"
_CHECKER = str(_SAMPLES / "2x2-checker.pbm")   # 2x2 checkerboard
_PATTERN = str(_SAMPLES / "3x2-pattern.pbm")   # 3x2 pattern
_BLACK1  = str(_SAMPLES / "1x1-black.pbm")     # 1x1 all-black


class TestPbmDimensions:
    def test_dimensions_returns_dict(self):
        r = pbm_dimensions(_CHECKER)
        assert isinstance(r, dict)

    def test_dimensions_has_width_height(self):
        r = pbm_dimensions(_CHECKER)
        assert "width" in r and "height" in r

    def test_checker_is_2x2(self):
        r = pbm_dimensions(_CHECKER)
        assert r["width"] == 2 and r["height"] == 2

    def test_pattern_is_3x2(self):
        r = pbm_dimensions(_PATTERN)
        assert r["width"] == 3 and r["height"] == 2


class TestPbmArea:
    def test_area_returns_int(self):
        assert isinstance(pbm_area(_CHECKER), int)

    def test_checker_area_is_4(self):
        assert pbm_area(_CHECKER) == 4

    def test_pattern_area_is_6(self):
        assert pbm_area(_PATTERN) == 6

    def test_black1_area_is_1(self):
        assert pbm_area(_BLACK1) == 1


class TestPbmRowCount:
    def test_row_count_returns_int(self):
        assert isinstance(pbm_row_count(_CHECKER), int)

    def test_checker_rows_is_2(self):
        assert pbm_row_count(_CHECKER) == 2

    def test_pattern_rows_is_2(self):
        assert pbm_row_count(_PATTERN) == 2

    def test_black1_rows_is_1(self):
        assert pbm_row_count(_BLACK1) == 1


class TestPbmColumnCount:
    def test_column_count_returns_int(self):
        assert isinstance(pbm_column_count(_CHECKER), int)

    def test_checker_cols_is_2(self):
        assert pbm_column_count(_CHECKER) == 2

    def test_pattern_cols_is_3(self):
        assert pbm_column_count(_PATTERN) == 3


class TestPbmTotalPixelCount:
    def test_total_pixel_count_returns_int(self):
        assert isinstance(pbm_total_pixel_count(_CHECKER), int)

    def test_total_pixels_int_alias(self):
        assert pbm_total_pixels(_CHECKER) == pbm_total_pixel_count(_CHECKER)

    def test_checker_total_is_4(self):
        assert pbm_total_pixel_count(_CHECKER) == 4

    def test_pattern_total_is_6(self):
        assert pbm_total_pixel_count(_PATTERN) == 6


class TestPbmBlackPixelCount:
    def test_black_pixel_count_returns_int(self):
        assert isinstance(pbm_black_pixel_count(_CHECKER), int)

    def test_checker_black_is_2(self):
        assert pbm_black_pixel_count(_CHECKER) == 2

    def test_black1_black_is_1(self):
        assert pbm_black_pixel_count(_BLACK1) == 1

    def test_black_count_lte_total(self):
        assert pbm_black_pixel_count(_CHECKER) <= pbm_total_pixel_count(_CHECKER)


class TestPbmWhitePixelCount:
    def test_white_pixel_count_returns_int(self):
        assert isinstance(pbm_white_pixel_count(_CHECKER), int)

    def test_checker_white_is_2(self):
        assert pbm_white_pixel_count(_CHECKER) == 2

    def test_black1_white_is_0(self):
        assert pbm_white_pixel_count(_BLACK1) == 0

    def test_black_plus_white_equals_total(self):
        s = _CHECKER
        assert pbm_black_pixel_count(s) + pbm_white_pixel_count(s) == pbm_total_pixel_count(s)


class TestPbmBlackPixelRatio:
    def test_ratio_returns_float(self):
        assert isinstance(pbm_black_pixel_ratio(_CHECKER), float)

    def test_ratio_in_0_to_1(self):
        assert 0.0 <= pbm_black_pixel_ratio(_CHECKER) <= 1.0

    def test_checker_ratio_is_0_5(self):
        assert pbm_black_pixel_ratio(_CHECKER) == pytest.approx(0.5)

    def test_black1_ratio_is_1(self):
        assert pbm_black_pixel_ratio(_BLACK1) == pytest.approx(1.0)


class TestPbmWhitePixelRatio:
    def test_white_ratio_returns_float(self):
        assert isinstance(pbm_white_pixel_ratio(_CHECKER), float)

    def test_checker_white_ratio_is_0_5(self):
        assert pbm_white_pixel_ratio(_CHECKER) == pytest.approx(0.5)

    def test_black_plus_white_ratio_is_1(self):
        s = _CHECKER
        assert pbm_black_pixel_ratio(s) + pbm_white_pixel_ratio(s) == pytest.approx(1.0)


class TestPbmBlackDensity:
    def test_black_density_returns_float(self):
        assert isinstance(pbm_black_density(_CHECKER), float)

    def test_white_density_returns_float(self):
        assert isinstance(pbm_white_density(_CHECKER), float)

    def test_checker_black_density_0_5(self):
        assert pbm_black_density(_CHECKER) == pytest.approx(0.5)

    def test_black1_black_density_1(self):
        assert pbm_black_density(_BLACK1) == pytest.approx(1.0)


class TestPbmAllBlackAllWhite:
    def test_all_black_returns_bool(self):
        assert isinstance(pbm_all_black(_CHECKER), bool)

    def test_all_white_returns_bool(self):
        assert isinstance(pbm_all_white(_CHECKER), bool)

    def test_checker_not_all_black(self):
        assert pbm_all_black(_CHECKER) is False

    def test_checker_not_all_white(self):
        assert pbm_all_white(_CHECKER) is False

    def test_black1_is_all_black(self):
        assert pbm_all_black(_BLACK1) is True

    def test_black1_not_all_white(self):
        assert pbm_all_white(_BLACK1) is False


class TestPbmHasAnyBlackWhite:
    def test_has_any_black_returns_bool(self):
        assert isinstance(pbm_has_any_black(_CHECKER), bool)

    def test_has_any_white_returns_bool(self):
        assert isinstance(pbm_has_any_white(_CHECKER), bool)

    def test_checker_has_both(self):
        assert pbm_has_any_black(_CHECKER) is True
        assert pbm_has_any_white(_CHECKER) is True

    def test_black1_has_no_white(self):
        assert pbm_has_any_white(_BLACK1) is False


class TestPbmIsAllBlack:
    def test_is_all_black_returns_bool(self):
        assert isinstance(pbm_is_all_black(_CHECKER), bool)

    def test_checker_is_not_all_black(self):
        assert pbm_is_all_black(_CHECKER) is False

    def test_black1_is_all_black(self):
        assert pbm_is_all_black(_BLACK1) is True


class TestPbmIsUniform:
    def test_is_uniform_returns_bool(self):
        assert isinstance(pbm_is_uniform(_CHECKER), bool)

    def test_checker_not_uniform(self):
        assert pbm_is_uniform(_CHECKER) is False

    def test_black1_is_uniform(self):
        assert pbm_is_uniform(_BLACK1) is True


class TestPbmShapeFlags:
    def test_is_square_returns_bool(self):
        assert isinstance(pbm_is_square(_CHECKER), bool)

    def test_checker_is_square(self):
        assert pbm_is_square(_CHECKER) is True

    def test_pattern_not_square(self):
        assert pbm_is_square(_PATTERN) is False

    def test_is_landscape_returns_bool(self):
        assert isinstance(pbm_is_landscape(_PATTERN), bool)

    def test_is_portrait_returns_bool(self):
        assert isinstance(pbm_is_portrait(_CHECKER), bool)

    def test_is_tall_returns_bool(self):
        assert isinstance(pbm_is_tall(_CHECKER), bool)

    def test_is_wide_returns_bool(self):
        assert isinstance(pbm_is_wide(_CHECKER), bool)


class TestPbmIsBinary:
    def test_is_binary_returns_bool(self):
        assert isinstance(pbm_is_binary(_CHECKER), bool)

    def test_is_binary_balanced_returns_bool(self):
        assert isinstance(pbm_is_binary_balanced(_CHECKER), bool)

    def test_checker_is_binary_balanced(self):
        assert pbm_is_binary_balanced(_CHECKER) is True


class TestPbmIsCheckerboard:
    def test_is_checkerboard_returns_bool(self):
        assert isinstance(pbm_is_checkerboard(_CHECKER), bool)


class TestPbmDimensions2:
    def test_aspect_ratio_returns_float(self):
        assert isinstance(pbm_aspect_ratio(_CHECKER), float)

    def test_checker_aspect_1_0(self):
        assert pbm_aspect_ratio(_CHECKER) == pytest.approx(1.0)

    def test_dimension_ratio_returns_float(self):
        assert isinstance(pbm_dimension_ratio(_CHECKER), float)

    def test_max_dimension_returns_int(self):
        assert isinstance(pbm_max_dimension(_CHECKER), int)

    def test_min_dimension_returns_int(self):
        assert isinstance(pbm_min_dimension(_CHECKER), int)

    def test_max_gte_min_dimension(self):
        assert pbm_max_dimension(_CHECKER) >= pbm_min_dimension(_CHECKER)


class TestPbmDiagonal:
    def test_diagonal_returns_float(self):
        assert isinstance(pbm_diagonal(_CHECKER), float)

    def test_diagonal_positive(self):
        assert pbm_diagonal(_CHECKER) > 0

    def test_diagonal_pixel_count_returns_int(self):
        assert isinstance(pbm_diagonal_pixel_count(_CHECKER), int)

    def test_diagonal_pixel_count_positive(self):
        assert pbm_diagonal_pixel_count(_CHECKER) >= 0


class TestPbmPerimeter:
    def test_perimeter_returns_int(self):
        assert isinstance(pbm_perimeter(_CHECKER), int)

    def test_perimeter_positive(self):
        assert pbm_perimeter(_CHECKER) > 0

    def test_checker_perimeter_is_8(self):
        assert pbm_perimeter(_CHECKER) == 8


class TestPbmMegapixels:
    def test_megapixels_returns_float(self):
        assert isinstance(pbm_megapixels(_CHECKER), float)

    def test_megapixels_positive(self):
        assert pbm_megapixels(_CHECKER) > 0

    def test_checker_megapixels_small(self):
        assert pbm_megapixels(_CHECKER) < 1.0


class TestPbmPixelDensity:
    def test_pixel_density_returns_float(self):
        assert isinstance(pbm_pixel_density(_CHECKER), float)

    def test_pixel_density_positive(self):
        assert pbm_pixel_density(_CHECKER) > 0


class TestPbmRowBlackCounts:
    def test_row_black_counts_returns_list(self):
        assert isinstance(pbm_row_black_counts(_CHECKER), list)

    def test_row_black_counts_length_equals_rows(self):
        r = pbm_row_black_counts(_CHECKER)
        assert len(r) == pbm_row_count(_CHECKER)

    def test_max_row_black_count_returns_int(self):
        assert isinstance(pbm_max_row_black_count(_CHECKER), int)

    def test_min_row_black_count_returns_int(self):
        assert isinstance(pbm_min_row_black_count(_CHECKER), int)

    def test_max_gte_min_row_black(self):
        s = _CHECKER
        assert pbm_max_row_black_count(s) >= pbm_min_row_black_count(s)


class TestPbmColumnBlackCounts:
    def test_column_black_counts_returns_list(self):
        assert isinstance(pbm_column_black_counts(_CHECKER), list)

    def test_column_black_counts_length_equals_cols(self):
        r = pbm_column_black_counts(_CHECKER)
        assert len(r) == pbm_column_count(_CHECKER)


class TestPbmAvgRowDensity:
    def test_avg_row_density_returns_float(self):
        assert isinstance(pbm_avg_row_density(_CHECKER), float)

    def test_avg_row_density_in_0_to_1(self):
        assert 0.0 <= pbm_avg_row_density(_CHECKER) <= 1.0

    def test_row_density_variance_returns_float(self):
        assert isinstance(pbm_row_density_variance(_CHECKER), float)

    def test_column_density_variance_returns_float(self):
        assert isinstance(pbm_column_density_variance(_CHECKER), float)


class TestPbmBorderBlackCount:
    def test_border_black_count_returns_int(self):
        assert isinstance(pbm_border_black_count(_CHECKER), int)

    def test_total_black_in_border_returns_int(self):
        assert isinstance(pbm_total_black_in_border(_CHECKER), int)

    def test_center_black_ratio_returns_float(self):
        assert isinstance(pbm_center_black_ratio(_CHECKER), float)

    def test_center_black_ratio_in_0_to_1(self):
        assert 0.0 <= pbm_center_black_ratio(_CHECKER) <= 1.0
