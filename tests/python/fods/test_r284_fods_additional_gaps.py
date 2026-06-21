"""
Tests for additional FODS analytics gap closure (8 FOSS gaps).
Closes: FODS_AVG_NUM, FODS_LONGEST, FODS_NUMERIC, FODS_CELL_TO,
        FODS_FORMULA, FODS_SHEET_R, FODS_TOTAL_T, FODS_COLUMN_
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fods import (
    parse_fods_strict,
    fods_avg_numeric_value,
    fods_longest_row_index,
    fods_numeric_sum_all,
    fods_cell_to_sheet_ratio,
    fods_formula_cell_count,
    fods_sheet_row_variance,
    fods_total_text_length,
    fods_column_count_variance,
)

_MINIMAL = _REPO / "samples/by-format/fods/minimal-spreadsheet.fods"
_MULTI = _REPO / "samples/by-format/fods/multi-sheet-basic.fods"
_FORMULA = _REPO / "samples/by-format/fods/formula-basic.fods"


def _wb(path):
    return parse_fods_strict(path)


class TestFodsAvgNumericValue:
    def test_returns_float(self):
        assert isinstance(fods_avg_numeric_value(_wb(_MINIMAL)), float)

    def test_nonnumeric_returns_zero(self):
        assert fods_avg_numeric_value(_wb(_MINIMAL)) == pytest.approx(0.0)

    def test_formula_sheet_has_value(self):
        assert fods_avg_numeric_value(_wb(_FORMULA)) == pytest.approx(30.0)

    def test_nonnegative(self):
        assert fods_avg_numeric_value(_wb(_MULTI)) >= 0.0


class TestFodsLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(fods_longest_row_index(_wb(_MINIMAL)), int)

    def test_nonnegative_or_minus_one(self):
        result = fods_longest_row_index(_wb(_MINIMAL))
        assert result >= -1

    def test_minimal_first_sheet(self):
        assert fods_longest_row_index(_wb(_MINIMAL)) == 0

    def test_formula_nonnegative(self):
        assert fods_longest_row_index(_wb(_FORMULA)) >= 0


class TestFodsNumericSumAll:
    def test_returns_float(self):
        assert isinstance(fods_numeric_sum_all(_wb(_MINIMAL)), float)

    def test_nonnumeric_returns_zero(self):
        assert fods_numeric_sum_all(_wb(_MINIMAL)) == pytest.approx(0.0)

    def test_formula_sheet_value(self):
        assert fods_numeric_sum_all(_wb(_FORMULA)) == pytest.approx(120.0)

    def test_nonnegative(self):
        assert fods_numeric_sum_all(_wb(_MULTI)) >= 0.0


class TestFodsCellToSheetRatio:
    def test_returns_float(self):
        assert isinstance(fods_cell_to_sheet_ratio(_wb(_MINIMAL)), float)

    def test_minimal_value(self):
        assert fods_cell_to_sheet_ratio(_wb(_MINIMAL)) == pytest.approx(1.0)

    def test_formula_value(self):
        assert fods_cell_to_sheet_ratio(_wb(_FORMULA)) == pytest.approx(4.0)

    def test_positive(self):
        assert fods_cell_to_sheet_ratio(_wb(_MULTI)) > 0.0


class TestFodsFormulaCellCount:
    def test_returns_int(self):
        assert isinstance(fods_formula_cell_count(_wb(_MINIMAL)), int)

    def test_minimal_no_formulas(self):
        assert fods_formula_cell_count(_wb(_MINIMAL)) == 0

    def test_formula_sheet_has_one(self):
        assert fods_formula_cell_count(_wb(_FORMULA)) == 1

    def test_nonnegative(self):
        assert fods_formula_cell_count(_wb(_MULTI)) >= 0


class TestFodsSheetRowVariance:
    def test_returns_float(self):
        assert isinstance(fods_sheet_row_variance(_wb(_MINIMAL)), float)

    def test_nonnegative(self):
        assert fods_sheet_row_variance(_wb(_MINIMAL)) >= 0.0

    def test_single_sheet_zero_variance(self):
        # minimal: only 1 sheet → variance = 0
        assert fods_sheet_row_variance(_wb(_MINIMAL)) == pytest.approx(0.0)

    def test_multi_sheet_variance(self):
        assert fods_sheet_row_variance(_wb(_MULTI)) == pytest.approx(0.25, rel=1e-3)


class TestFodsTotalTextLength:
    def test_returns_int(self):
        assert isinstance(fods_total_text_length(_wb(_MINIMAL)), int)

    def test_nonnegative(self):
        assert fods_total_text_length(_wb(_MINIMAL)) >= 0

    def test_minimal_value(self):
        assert fods_total_text_length(_wb(_MINIMAL)) == 5

    def test_multi_larger_than_minimal(self):
        assert fods_total_text_length(_wb(_MULTI)) > fods_total_text_length(_wb(_MINIMAL))


class TestFodsColumnCountVariance:
    def test_returns_float(self):
        assert isinstance(fods_column_count_variance(_wb(_MINIMAL)), float)

    def test_nonnegative(self):
        assert fods_column_count_variance(_wb(_MINIMAL)) >= 0.0

    def test_single_sheet_zero(self):
        assert fods_column_count_variance(_wb(_MINIMAL)) == pytest.approx(0.0)

    def test_multi_value(self):
        assert fods_column_count_variance(_wb(_MULTI)) == pytest.approx(0.25, rel=1e-3)
