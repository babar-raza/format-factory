"""Tests for gnumeric_is_all_string and gnumeric_avg_string_cells_per_sheet (Sprint 93, R303)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.gnumeric.gnumeric_codec import gnumeric_is_all_string, gnumeric_avg_string_cells_per_sheet

GN = _REPO / "samples" / "by-format" / "gnumeric"


def test_is_all_string_minimal():
    assert gnumeric_is_all_string(GN / "minimal-spreadsheet.gnumeric") is True


def test_is_all_string_multi_cell():
    assert gnumeric_is_all_string(GN / "multi-cell-basic.gnumeric") is False


def test_is_all_string_empty():
    assert gnumeric_is_all_string(GN / "empty-sheet.gnumeric") is False


def test_is_all_string_returns_bool():
    assert isinstance(gnumeric_is_all_string(GN / "minimal-spreadsheet.gnumeric"), bool)


def test_is_all_string_false_for_mixed():
    # multi-cell has numeric + string cells
    assert gnumeric_is_all_string(GN / "multi-cell-basic.gnumeric") is False


def test_avg_string_cells_minimal():
    assert abs(gnumeric_avg_string_cells_per_sheet(GN / "minimal-spreadsheet.gnumeric") - 1.0) < 0.01


def test_avg_string_cells_multi():
    assert abs(gnumeric_avg_string_cells_per_sheet(GN / "multi-cell-basic.gnumeric") - 3.0) < 0.01


def test_avg_string_cells_empty():
    assert abs(gnumeric_avg_string_cells_per_sheet(GN / "empty-sheet.gnumeric") - 0.0) < 0.01


def test_avg_string_cells_returns_float():
    assert isinstance(gnumeric_avg_string_cells_per_sheet(GN / "minimal-spreadsheet.gnumeric"), float)


def test_avg_string_cells_nonnegative():
    assert gnumeric_avg_string_cells_per_sheet(GN / "empty-sheet.gnumeric") >= 0.0
