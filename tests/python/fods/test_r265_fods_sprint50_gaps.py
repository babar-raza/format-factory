"""Tests for FODS Sprint 50 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_CELL_CO-001  (Fods Cell Count Variance)
  GAP-FODS-FOSS-FODS_ROW_WID-001  (Fods Row Width Variance)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import parse_fods_strict, fods_cell_count_variance, fods_row_width_variance

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


class TestFodsCellCountVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_cell_count_variance(wb), (int, float))

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_count_variance(wb) == 0.0

    def test_zero_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_cell_count_variance(wb) == 0.0

    def test_zero_for_multi_sheet(self):
        wb = parse_fods_strict(_MULTI)
        assert fods_cell_count_variance(wb) == 0.0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_count_variance(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_cell_count_variance(wb) == fods_cell_count_variance(wb)


class TestFodsRowWidthVariance:
    def test_return_type(self):
        wb = parse_fods_strict(_MINIMAL)
        assert isinstance(fods_row_width_variance(wb), (int, float))

    def test_zero_for_minimal(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_width_variance(wb) == 0.0

    def test_zero_for_formula(self):
        wb = parse_fods_strict(_FORMULA)
        assert fods_row_width_variance(wb) == 0.0

    def test_zero_for_typed_values(self):
        wb = parse_fods_strict(_TYPED)
        assert fods_row_width_variance(wb) == 0.0

    def test_nonnegative(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_width_variance(wb) >= 0

    def test_consistent_across_calls(self):
        wb = parse_fods_strict(_MINIMAL)
        assert fods_row_width_variance(wb) == fods_row_width_variance(wb)
