"""Tests for fods_row_to_sheet_ratio and fods_has_formula_cells (Sprint r305)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods.neutral_model import fods_row_to_sheet_ratio, fods_has_formula_cells
from src.python.fods import parse_fods

_FODS = _REPO / "samples" / "by-format" / "fods"


def _wb(name):
    return parse_fods(_FODS / name)


class TestFodsRowToSheetRatio:
    """Tests for fods_row_to_sheet_ratio."""

    def test_minimal_one_row_one_sheet(self):
        """minimal-spreadsheet.fods: 1 row / 1 sheet = 1.0."""
        assert fods_row_to_sheet_ratio(_wb("minimal-spreadsheet.fods")) == 1.0

    def test_multi_sheet_ratio(self):
        """multi-sheet-basic.fods: 3 rows / 2 sheets = 1.5."""
        assert fods_row_to_sheet_ratio(_wb("multi-sheet-basic.fods")) == 1.5

    def test_typed_values_ratio(self):
        """typed-values-basic.fods: 4 rows / 1 sheet = 4.0."""
        assert fods_row_to_sheet_ratio(_wb("typed-values-basic.fods")) == 4.0

    def test_returns_float(self):
        assert isinstance(fods_row_to_sheet_ratio(_wb("minimal-spreadsheet.fods")), float)

    def test_multi_sheet_greater_than_minimal(self):
        r1 = fods_row_to_sheet_ratio(_wb("minimal-spreadsheet.fods"))
        r2 = fods_row_to_sheet_ratio(_wb("multi-sheet-basic.fods"))
        assert r2 > r1

    def test_typed_greater_than_multi(self):
        r1 = fods_row_to_sheet_ratio(_wb("multi-sheet-basic.fods"))
        r2 = fods_row_to_sheet_ratio(_wb("typed-values-basic.fods"))
        assert r2 > r1


class TestFodsHasFormulaCells:
    """Tests for fods_has_formula_cells."""

    def test_minimal_no_formulas(self):
        """minimal-spreadsheet.fods has no formulas → False."""
        assert fods_has_formula_cells(_wb("minimal-spreadsheet.fods")) is False

    def test_multi_sheet_no_formulas(self):
        """multi-sheet-basic.fods has no formulas → False."""
        assert fods_has_formula_cells(_wb("multi-sheet-basic.fods")) is False

    def test_formula_basic_has_formula(self):
        """formula-basic.fods has at least 1 formula → True."""
        assert fods_has_formula_cells(_wb("formula-basic.fods")) is True

    def test_returns_bool(self):
        assert isinstance(fods_has_formula_cells(_wb("formula-basic.fods")), bool)

    def test_non_formula_files_are_false(self):
        for name in ["minimal-spreadsheet.fods", "multi-sheet-basic.fods"]:
            assert fods_has_formula_cells(_wb(name)) is False

    def test_formula_true_minimal_false(self):
        r1 = fods_has_formula_cells(_wb("formula-basic.fods"))
        r2 = fods_has_formula_cells(_wb("minimal-spreadsheet.fods"))
        assert r1 is True and r2 is False
