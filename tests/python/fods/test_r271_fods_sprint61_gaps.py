"""Tests for FODS Sprint 61 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_SHEET_C-001   (Fods Sheet Cell Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_sheet_cell_variance

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsSheetCellVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_sheet_cell_variance(wb), (int, float))

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_sheet_cell_variance(wb) == 0.0

    def test_zero_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_sheet_cell_variance(wb) == 0.0

    def test_exact_2_25_for_multi(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_sheet_cell_variance(wb) == 2.25

    def test_zero_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_sheet_cell_variance(wb) == 0.0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_sheet_cell_variance(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_sheet_cell_variance(wb) == fods_sheet_cell_variance(wb)
