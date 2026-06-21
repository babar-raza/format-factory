"""Tests for gnumeric_string_cell_percentage and gnumeric_cells_per_row (Sprint 106, R316)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import gnumeric_string_cell_percentage, gnumeric_cells_per_row

GNU = _REPO / "samples" / "by-format" / "gnumeric"


def test_string_pct_minimal():
    assert abs(gnumeric_string_cell_percentage(GNU / "minimal-spreadsheet.gnumeric") - 100.0) < 0.1


def test_string_pct_multi_cell():
    assert abs(gnumeric_string_cell_percentage(GNU / "multi-cell-basic.gnumeric") - 75.0) < 0.1


def test_string_pct_empty():
    assert abs(gnumeric_string_cell_percentage(GNU / "empty-sheet.gnumeric") - 0.0) < 0.1


def test_string_pct_returns_float():
    assert isinstance(gnumeric_string_cell_percentage(GNU / "minimal-spreadsheet.gnumeric"), float)


def test_string_pct_bounded():
    pct = gnumeric_string_cell_percentage(GNU / "minimal-spreadsheet.gnumeric")
    assert 0.0 <= pct <= 100.0


def test_cells_per_row_minimal():
    assert abs(gnumeric_cells_per_row(GNU / "minimal-spreadsheet.gnumeric") - 1.0) < 0.01


def test_cells_per_row_multi_cell():
    assert abs(gnumeric_cells_per_row(GNU / "multi-cell-basic.gnumeric") - 2.0) < 0.01


def test_cells_per_row_empty():
    assert abs(gnumeric_cells_per_row(GNU / "empty-sheet.gnumeric") - 0.0) < 0.01


def test_cells_per_row_returns_float():
    assert isinstance(gnumeric_cells_per_row(GNU / "minimal-spreadsheet.gnumeric"), float)


def test_cells_per_row_positive():
    assert gnumeric_cells_per_row(GNU / "multi-cell-basic.gnumeric") > 0.0
