"""Tests for gnumeric_has_string_cells and gnumeric_has_numeric_cells (Sprint 76)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import gnumeric_has_string_cells, gnumeric_has_numeric_cells

GN = _REPO / "samples" / "by-format" / "gnumeric"


# --- gnumeric_has_string_cells ---

def test_has_string_cells_minimal_true():
    assert gnumeric_has_string_cells(GN / "minimal-spreadsheet.gnumeric") is True


def test_has_string_cells_multi_cell_true():
    assert gnumeric_has_string_cells(GN / "multi-cell-basic.gnumeric") is True


def test_has_string_cells_empty_false():
    assert gnumeric_has_string_cells(GN / "empty-sheet.gnumeric") is False


def test_has_string_cells_returns_bool():
    assert isinstance(gnumeric_has_string_cells(GN / "minimal-spreadsheet.gnumeric"), bool)


def test_has_string_cells_empty_is_false():
    assert gnumeric_has_string_cells(GN / "empty-sheet.gnumeric") is False


# --- gnumeric_has_numeric_cells ---

def test_has_numeric_cells_minimal_false():
    assert gnumeric_has_numeric_cells(GN / "minimal-spreadsheet.gnumeric") is False


def test_has_numeric_cells_multi_cell_true():
    assert gnumeric_has_numeric_cells(GN / "multi-cell-basic.gnumeric") is True


def test_has_numeric_cells_empty_false():
    assert gnumeric_has_numeric_cells(GN / "empty-sheet.gnumeric") is False


def test_has_numeric_cells_returns_bool():
    assert isinstance(gnumeric_has_numeric_cells(GN / "multi-cell-basic.gnumeric"), bool)


def test_has_numeric_cells_differs_from_has_string():
    # minimal has strings but not numeric
    assert gnumeric_has_string_cells(GN / "minimal-spreadsheet.gnumeric") is True
    assert gnumeric_has_numeric_cells(GN / "minimal-spreadsheet.gnumeric") is False
