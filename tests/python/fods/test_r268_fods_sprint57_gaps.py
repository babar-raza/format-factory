"""Tests for FODS Sprint 57 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_ROW_TO_-001   (Fods Row To Sheet Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_row_to_sheet_ratio

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsRowToSheetRatio:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_row_to_sheet_ratio(wb), float)

    def test_exact_1_0_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_to_sheet_ratio(wb) == 1.0

    def test_exact_4_0_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_row_to_sheet_ratio(wb) == 4.0

    def test_exact_1_5_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_row_to_sheet_ratio(wb) == 1.5

    def test_exact_4_0_for_typed(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_row_to_sheet_ratio(wb) == 4.0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_to_sheet_ratio(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_to_sheet_ratio(wb) == fods_row_to_sheet_ratio(wb)
