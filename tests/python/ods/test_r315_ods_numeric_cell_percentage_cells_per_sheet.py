"""Tests for ods_numeric_cell_percentage and ods_cells_per_sheet (Sprint 105, R315)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ods.ods_parser import ods_numeric_cell_percentage, ods_cells_per_sheet

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


def test_numeric_pct_minimal():
    assert abs(ods_numeric_cell_percentage(ODS / "minimal-spreadsheet.ods") - 25.0) < 0.1


def test_numeric_pct_numeric_row():
    assert abs(ods_numeric_cell_percentage(ODS / "numeric-row.ods") - 100.0) < 0.1


def test_numeric_pct_single():
    assert abs(ods_numeric_cell_percentage(ODS / "single-cell.ods") - 0.0) < 0.1


def test_numeric_pct_returns_float():
    assert isinstance(ods_numeric_cell_percentage(ODS / "minimal-spreadsheet.ods"), float)


def test_numeric_pct_bounded():
    pct = ods_numeric_cell_percentage(ODS / "minimal-spreadsheet.ods")
    assert 0.0 <= pct <= 100.0


def test_cells_per_sheet_minimal():
    assert abs(ods_cells_per_sheet(ODS / "minimal-spreadsheet.ods") - 4.0) < 0.01


def test_cells_per_sheet_numeric():
    assert abs(ods_cells_per_sheet(ODS / "numeric-row.ods") - 3.0) < 0.01


def test_cells_per_sheet_single():
    assert abs(ods_cells_per_sheet(ODS / "single-cell.ods") - 1.0) < 0.01


def test_cells_per_sheet_returns_float():
    assert isinstance(ods_cells_per_sheet(ODS / "minimal-spreadsheet.ods"), float)


def test_cells_per_sheet_positive():
    assert ods_cells_per_sheet(ODS / "numeric-row.ods") > 0.0
