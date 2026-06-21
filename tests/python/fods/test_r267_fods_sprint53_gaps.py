"""Tests for FODS Sprint 53 gap closure.

Closes:
  GAP-FODS-FOSS-FODS_CELLS_P-001  (Fods Cells Per Sheet Avg)
  GAP-FODS-FOSS-FODS_IS_FULL-001  (Fods Is Fully Numeric)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fods import fods_cells_per_sheet_avg, fods_is_fully_numeric

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_FORMULA = str(_DIR / "formula-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")


class TestFodsCellsPerSheetAvg:
    def test_return_type(self):
        assert isinstance(fods_cells_per_sheet_avg(_MINIMAL), (int, float))

    def test_exact_1_for_minimal(self):
        assert fods_cells_per_sheet_avg(_MINIMAL) == 1.0

    def test_exact_4_for_formula(self):
        assert fods_cells_per_sheet_avg(_FORMULA) == 4.0

    def test_exact_8_for_typed(self):
        assert fods_cells_per_sheet_avg(_TYPED) == 8.0

    def test_exact_2_5_for_multi(self):
        assert fods_cells_per_sheet_avg(_MULTI) == 2.5

    def test_positive(self):
        assert fods_cells_per_sheet_avg(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert fods_cells_per_sheet_avg(_MINIMAL) == fods_cells_per_sheet_avg(_MINIMAL)


class TestFodsIsFullyNumeric:
    def test_return_type(self):
        assert isinstance(fods_is_fully_numeric(_MINIMAL), bool)

    def test_false_for_minimal(self):
        assert fods_is_fully_numeric(_MINIMAL) is False

    def test_true_for_formula(self):
        assert fods_is_fully_numeric(_FORMULA) is True

    def test_false_for_typed(self):
        assert fods_is_fully_numeric(_TYPED) is False

    def test_false_for_multi(self):
        assert fods_is_fully_numeric(_MULTI) is False

    def test_consistent_across_calls(self):
        assert fods_is_fully_numeric(_MINIMAL) == fods_is_fully_numeric(_MINIMAL)
