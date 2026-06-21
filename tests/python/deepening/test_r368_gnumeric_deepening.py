"""Tests for Gnumeric product deepening sprint 139.

New functions:
  gnumeric_nonempty_cells_per_row   — avg nonempty cells per row in first sheet
  gnumeric_string_to_nonempty_ratio — ratio of string cells to all nonempty cells
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.gnumeric import (
    gnumeric_nonempty_cells_per_row,
    gnumeric_string_to_nonempty_ratio,
)

_EMPTY = str(_REPO / "samples" / "by-format" / "gnumeric" / "empty-sheet.gnumeric")
_MINIMAL = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")
_MULTI = str(_REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric")


class TestGnumericNonemptyCellsPerRow:
    def test_return_type(self):
        assert isinstance(gnumeric_nonempty_cells_per_row(_MINIMAL), float)

    def test_zero_for_empty_sheet(self):
        assert gnumeric_nonempty_cells_per_row(_EMPTY) == 0.0

    def test_exact_1_for_minimal(self):
        # minimal-spreadsheet: 1 nonempty cell / 1 row = 1.0
        assert gnumeric_nonempty_cells_per_row(_MINIMAL) == 1.0

    def test_exact_2_for_multi(self):
        # multi-cell-basic: 4 nonempty cells / 2 rows = 2.0
        assert gnumeric_nonempty_cells_per_row(_MULTI) == 2.0

    def test_nonnegative(self):
        assert gnumeric_nonempty_cells_per_row(_EMPTY) >= 0.0

    def test_consistent(self):
        assert gnumeric_nonempty_cells_per_row(_MULTI) == gnumeric_nonempty_cells_per_row(_MULTI)


class TestGnumericStringToNonemptyRatio:
    def test_return_type(self):
        assert isinstance(gnumeric_string_to_nonempty_ratio(_MINIMAL), float)

    def test_zero_for_empty_sheet(self):
        assert gnumeric_string_to_nonempty_ratio(_EMPTY) == 0.0

    def test_exact_1_for_minimal(self):
        # minimal-spreadsheet: all values are strings in cell_grid
        assert gnumeric_string_to_nonempty_ratio(_MINIMAL) == 1.0

    def test_exact_1_for_multi(self):
        # multi-cell-basic: all 4 values stored as strings (including numeric '42')
        assert gnumeric_string_to_nonempty_ratio(_MULTI) == 1.0

    def test_bounded(self):
        r = gnumeric_string_to_nonempty_ratio(_MULTI)
        assert 0.0 <= r <= 1.0

    def test_consistent(self):
        assert gnumeric_string_to_nonempty_ratio(_MULTI) == gnumeric_string_to_nonempty_ratio(_MULTI)
