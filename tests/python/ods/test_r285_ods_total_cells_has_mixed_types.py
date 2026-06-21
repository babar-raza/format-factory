"""Tests for ods_total_cells and ods_has_mixed_types (Sprint 75)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import ods_total_cells, ods_has_mixed_types

ODS = _REPO / "samples" / "by-format" / "ods" / "valid"


# --- ods_total_cells ---

def test_total_cells_minimal_spreadsheet():
    assert ods_total_cells(ODS / "minimal-spreadsheet.ods") == 4


def test_total_cells_numeric_row():
    assert ods_total_cells(ODS / "numeric-row.ods") == 3


def test_total_cells_single_cell():
    assert ods_total_cells(ODS / "single-cell.ods") == 1


def test_total_cells_returns_int():
    assert isinstance(ods_total_cells(ODS / "minimal-spreadsheet.ods"), int)


def test_total_cells_greater_than_zero():
    assert ods_total_cells(ODS / "minimal-spreadsheet.ods") > 0


# --- ods_has_mixed_types ---

def test_has_mixed_types_minimal_true():
    assert ods_has_mixed_types(ODS / "minimal-spreadsheet.ods") is True


def test_has_mixed_types_numeric_row_false():
    assert ods_has_mixed_types(ODS / "numeric-row.ods") is False


def test_has_mixed_types_single_cell_false():
    assert ods_has_mixed_types(ODS / "single-cell.ods") is False


def test_has_mixed_types_returns_bool():
    assert isinstance(ods_has_mixed_types(ODS / "minimal-spreadsheet.ods"), bool)


def test_has_mixed_types_consistent_with_total():
    # only minimal-spreadsheet has mixed types (string + numeric)
    assert ods_has_mixed_types(ODS / "minimal-spreadsheet.ods") is True
    assert ods_total_cells(ODS / "minimal-spreadsheet.ods") > ods_total_cells(ODS / "single-cell.ods")
