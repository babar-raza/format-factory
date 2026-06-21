"""Tests for FODS Sprint 45 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_MAX_NUM-001  (Fods Max Numeric All Sheets)
  GAP-FODS-FOSS-FODS_MIN_NUM-001  (Fods Min Numeric All Sheets)
  GAP-FODS-FOSS-FODS_UNIQUE_-001  (Fods Unique String Count)
  GAP-FODS-FOSS-FODS_BOOLEAN-001  (Fods Boolean Cell Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    fods_max_numeric_all_sheets,
    fods_min_numeric_all_sheets,
    fods_unique_string_count,
    fods_boolean_cell_count,
    parse_fods_strict,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_FORMULA = str(_DIR / "formula-basic.fods")
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsMaxNumericAllSheets:
    def test_return_type(self):
        doc = parse_fods_strict(_FORMULA)
        assert isinstance(fods_max_numeric_all_sheets(doc), float)

    def test_exact_60_for_formula_basic(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_max_numeric_all_sheets(doc) == 60.0

    def test_exact_42_5_for_typed_values(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_max_numeric_all_sheets(doc) == 42.5

    def test_zero_for_minimal(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_max_numeric_all_sheets(doc) == 0.0

    def test_consistent_across_calls(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_max_numeric_all_sheets(doc) == fods_max_numeric_all_sheets(doc)


class TestFodsMinNumericAllSheets:
    def test_return_type(self):
        doc = parse_fods_strict(_FORMULA)
        assert isinstance(fods_min_numeric_all_sheets(doc), float)

    def test_exact_10_for_formula_basic(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_min_numeric_all_sheets(doc) == 10.0

    def test_exact_42_5_for_typed_values(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_min_numeric_all_sheets(doc) == 42.5

    def test_zero_for_minimal(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_min_numeric_all_sheets(doc) == 0.0

    def test_min_lte_max(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_min_numeric_all_sheets(doc) <= fods_max_numeric_all_sheets(doc)


class TestFodsUniqueStringCount:
    def test_return_type(self):
        doc = parse_fods_strict(_MULTI)
        assert isinstance(fods_unique_string_count(doc), int)

    def test_exact_5_for_multi_sheet(self):
        doc = parse_fods_strict(_MULTI)
        assert fods_unique_string_count(doc) == 5

    def test_exact_6_for_typed_values(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_unique_string_count(doc) == 6

    def test_exact_1_for_minimal(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_unique_string_count(doc) == 1

    def test_nonnegative(self):
        doc = parse_fods_strict(_MULTI)
        assert fods_unique_string_count(doc) >= 0


class TestFodsBooleanCellCount:
    def test_return_type(self):
        doc = parse_fods_strict(_TYPED)
        assert isinstance(fods_boolean_cell_count(doc), int)

    def test_exact_1_for_typed_values(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_boolean_cell_count(doc) == 1

    def test_zero_for_formula_basic(self):
        doc = parse_fods_strict(_FORMULA)
        assert fods_boolean_cell_count(doc) == 0

    def test_zero_for_minimal(self):
        doc = parse_fods_strict(_MINIMAL)
        assert fods_boolean_cell_count(doc) == 0

    def test_nonnegative(self):
        doc = parse_fods_strict(_TYPED)
        assert fods_boolean_cell_count(doc) >= 0
