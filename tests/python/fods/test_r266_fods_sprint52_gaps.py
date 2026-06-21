"""Tests for FODS Sprint 52 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_TOTAL_S-001  (Fods Total String Cells)
  GAP-FODS-FOSS-FODS_MAX_COL-001  (Fods Max Column Index)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_total_string_cells, fods_max_column_index

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")


class TestFodsTotalStringCells:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_total_string_cells(wb), int)

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_total_string_cells(wb) == 0

    def test_zero_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_total_string_cells(wb) == 0

    def test_zero_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_total_string_cells(wb) == 0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_total_string_cells(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_total_string_cells(wb) == fods_total_string_cells(wb)


class TestFodsMaxColumnIndex:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_max_column_index(wb), int)

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_column_index(wb) == 0

    def test_zero_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_max_column_index(wb) == 0

    def test_exact_1_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_max_column_index(wb) == 1

    def test_exact_1_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_max_column_index(wb) == 1

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_column_index(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_max_column_index(wb) == fods_max_column_index(wb)
