"""Tests for FODS gap closure (Sprint 40).

Closes:
  GAP-FODS-FOSS-FODS_HAS_STR-001  (Fods Has String Cells)
  GAP-FODS-FOSS-FODS_ROW_COU-001  (Fods Row Count Variance)
  GAP-FODS-FOSS-FODS_AVG_STR-001  (Fods Avg String Length)
  GAP-FODS-FOSS-FODS_COL_COU-001  (Fods Col Count Variance)
  GAP-FODS-FOSS-FODS_AVG_NUM-001  (Fods Avg Numeric Value)
  GAP-FODS-FOSS-FODS_LONGEST-001  (Fods Longest Row Index)
  GAP-FODS-FOSS-FODS_NUMERIC-001  (Fods Numeric Sum All)
  GAP-FODS-FOSS-FODS_CELL_TO-001  (Fods Cell To Sheet Ratio)
  GAP-FODS-FOSS-FODS_FORMULA-001  (Fods Formula Cell Count)
  GAP-FODS-FOSS-FODS_SHEET_R-001  (Fods Sheet Row Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    fods_avg_numeric_value,
    fods_avg_string_length,
    fods_cell_to_sheet_ratio,
    fods_col_count_variance,
    fods_formula_cell_count,
    fods_has_string_cells,
    fods_longest_row_index,
    fods_numeric_sum_all,
    fods_row_count_variance,
    fods_sheet_row_variance,
    parse_fods_strict,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_FORMULA = str(_DIR / "formula-basic.fods")
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_MULTI_SHEET = str(_DIR / "multi-sheet-basic.fods")


class TestFodsHasStringCells:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_has_string_cells(wb), bool)

    def test_false_for_formula_only(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_has_string_cells(wb) is False

    def test_true_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_has_string_cells(wb) is True

    def test_true_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_has_string_cells(wb) is True

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_has_string_cells(wb) == fods_has_string_cells(wb)


class TestFodsRowCountVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_row_count_variance(wb), float)

    def test_zero_for_single_sheet_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_row_count_variance(wb) == 0.0

    def test_nonzero_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_row_count_variance(wb) == 0.25

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_row_count_variance(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_row_count_variance(wb) == fods_row_count_variance(wb)


class TestFodsAvgStringLength:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_avg_string_length(wb), float)

    def test_nonnegative_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_avg_string_length(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_avg_string_length(wb) == fods_avg_string_length(wb)


class TestFodsColCountVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_col_count_variance(wb), float)

    def test_zero_for_single_sheet(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_col_count_variance(wb) == 0.0

    def test_nonzero_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_col_count_variance(wb) == 0.25

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_col_count_variance(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_col_count_variance(wb) == fods_col_count_variance(wb)


class TestFodsAvgNumericValue:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_avg_numeric_value(wb), float)

    def test_exact_30_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_avg_numeric_value(wb) == 30.0

    def test_zero_for_minimal_no_numbers(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_avg_numeric_value(wb) == 0.0

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_avg_numeric_value(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_avg_numeric_value(wb) == fods_avg_numeric_value(wb)


class TestFodsLongestRowIndex:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_longest_row_index(wb), int)

    def test_exact_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_longest_row_index(wb) == 0

    def test_exact_0_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_longest_row_index(wb) == 0

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_longest_row_index(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_longest_row_index(wb) == fods_longest_row_index(wb)


class TestFodsNumericSumAll:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_numeric_sum_all(wb), float)

    def test_exact_120_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_numeric_sum_all(wb) == 120.0

    def test_zero_for_minimal_no_numbers(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_numeric_sum_all(wb) == 0.0

    def test_nonnegative_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_numeric_sum_all(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_numeric_sum_all(wb) == fods_numeric_sum_all(wb)


class TestFodsCellToSheetRatio:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_cell_to_sheet_ratio(wb), float)

    def test_exact_4_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_to_sheet_ratio(wb) == 4.0

    def test_exact_1_0_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_to_sheet_ratio(wb) == 1.0

    def test_exact_2_5_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_cell_to_sheet_ratio(wb) == 2.5

    def test_positive(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_to_sheet_ratio(wb) > 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_to_sheet_ratio(wb) == fods_cell_to_sheet_ratio(wb)


class TestFodsFormulaCellCount:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_formula_cell_count(wb), int)

    def test_exact_1_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_formula_cell_count(wb) == 1

    def test_zero_for_minimal_no_formulas(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_formula_cell_count(wb) == 0

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_formula_cell_count(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_formula_cell_count(wb) == fods_formula_cell_count(wb)


class TestFodsSheetRowVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_FORMULA)
        assert isinstance(fods_sheet_row_variance(wb), float)

    def test_zero_for_single_sheet(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_sheet_row_variance(wb) == 0.0

    def test_nonzero_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_sheet_row_variance(wb) == 0.25

    def test_nonnegative(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_sheet_row_variance(wb) >= 0.0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MULTI_SHEET)
        assert fods_sheet_row_variance(wb) == fods_sheet_row_variance(wb)
