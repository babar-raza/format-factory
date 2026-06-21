"""
FODS FOSS gap closure tests.

Closes:
  GAP-FODS-FOSS-FODS_HAS_STR-001  — fods_has_string_cells
  GAP-FODS-FOSS-FODS_ROW_COU-001  — fods_row_count_variance
  GAP-FODS-FOSS-FODS_AVG_STR-001  — fods_avg_string_length
  GAP-FODS-FOSS-FODS_COL_COU-001  — fods_col_count_variance
  GAP-FODS-FOSS-FODS_AVG_NUM-001  — fods_avg_numeric_value
  GAP-FODS-FOSS-FODS_LONGEST-001  — fods_longest_row_index
  GAP-FODS-FOSS-FODS_NUMERIC-001  — fods_numeric_sum_all
  GAP-FODS-FOSS-FODS_CELL_TO-001  — fods_cell_to_sheet_ratio
  GAP-FODS-FOSS-FODS_FORMULA-001  — fods_formula_cell_count
  GAP-FODS-FOSS-FODS_SHEET_R-001  — fods_sheet_row_variance

Run from repo root:
    python -m pytest tests/python/fods/test_fods_gap_closure_foss.py -v
"""

import sys
import pytest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from fods.parser import parse_fods
import fods

SAMPLES = REPO_ROOT / "samples" / "by-format" / "fods"
MINIMAL = SAMPLES / "minimal-spreadsheet.fods"
FORMULA = SAMPLES / "formula-basic.fods"
MULTI = SAMPLES / "multi-sheet-basic.fods"

WB_MINIMAL = parse_fods(MINIMAL)
WB_FORMULA = parse_fods(FORMULA)
WB_MULTI = parse_fods(MULTI)


class TestFodsHasStringCells:
    def test_minimal_has_string(self):
        assert fods.fods_has_string_cells(WB_MINIMAL) is True

    def test_formula_no_string(self):
        assert fods.fods_has_string_cells(WB_FORMULA) is False

    def test_returns_bool(self):
        assert isinstance(fods.fods_has_string_cells(WB_MINIMAL), bool)


class TestFodsRowCountVariance:
    def test_returns_numeric(self):
        assert isinstance(fods.fods_row_count_variance(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_row_count_variance(wb) >= 0


class TestFodsAvgStringLength:
    def test_returns_numeric(self):
        assert isinstance(fods.fods_avg_string_length(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_avg_string_length(wb) >= 0


class TestFodsColCountVariance:
    def test_returns_numeric(self):
        assert isinstance(fods.fods_col_count_variance(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_col_count_variance(wb) >= 0


class TestFodsAvgNumericValue:
    def test_formula_has_numeric(self):
        assert fods.fods_avg_numeric_value(WB_FORMULA) == pytest.approx(30.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(fods.fods_avg_numeric_value(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_avg_numeric_value(wb) >= 0


class TestFodsLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(fods.fods_longest_row_index(WB_MINIMAL), int)

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_longest_row_index(wb) >= 0


class TestFodsNumericSumAll:
    def test_formula_has_sum(self):
        assert fods.fods_numeric_sum_all(WB_FORMULA) == pytest.approx(120.0, abs=0.01)

    def test_returns_numeric(self):
        assert isinstance(fods.fods_numeric_sum_all(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA]:
            assert fods.fods_numeric_sum_all(wb) >= 0


class TestFodsCellToSheetRatio:
    def test_returns_numeric(self):
        assert isinstance(fods.fods_cell_to_sheet_ratio(WB_MINIMAL), (int, float))

    def test_positive(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_cell_to_sheet_ratio(wb) > 0


class TestFodsFormulaCellCount:
    def test_formula_has_one(self):
        assert fods.fods_formula_cell_count(WB_FORMULA) == 1

    def test_minimal_none(self):
        assert fods.fods_formula_cell_count(WB_MINIMAL) == 0

    def test_returns_int(self):
        assert isinstance(fods.fods_formula_cell_count(WB_MINIMAL), int)

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_formula_cell_count(wb) >= 0


class TestFodsSheetRowVariance:
    def test_returns_numeric(self):
        assert isinstance(fods.fods_sheet_row_variance(WB_MINIMAL), (int, float))

    def test_non_negative(self):
        for wb in [WB_MINIMAL, WB_FORMULA, WB_MULTI]:
            assert fods.fods_sheet_row_variance(wb) >= 0
