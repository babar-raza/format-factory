"""Tests for 6 new functions in ods_stats (ext4 batch)."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

import pytest

from ods.ods_stats import (
    ods_avg_sheet_row_count,
    ods_total_cell_count,
    ods_is_multi_sheet,
    ods_last_sheet_row_count,
    ods_has_text_cells,
    ods_sheet_names_list,
)

VALID = _REPO / "samples" / "by-format" / "ods" / "valid"
MINIMAL = VALID / "minimal-spreadsheet.ods"
NUMERIC = VALID / "numeric-row.ods"
SINGLE = VALID / "single-cell.ods"


# --- ods_avg_sheet_row_count ---

def test_avg_sheet_row_count_minimal():
    result = ods_avg_sheet_row_count(MINIMAL)
    assert result == 2.0


def test_avg_sheet_row_count_numeric():
    assert ods_avg_sheet_row_count(NUMERIC) == 1.0


def test_avg_sheet_row_count_single():
    result = ods_avg_sheet_row_count(SINGLE)
    assert isinstance(result, float)
    assert result >= 0.0


# --- ods_total_cell_count ---

def test_total_cell_count_minimal():
    assert ods_total_cell_count(MINIMAL) == 4


def test_total_cell_count_numeric():
    assert ods_total_cell_count(NUMERIC) == 3


def test_total_cell_count_single():
    assert ods_total_cell_count(SINGLE) == 1


# --- ods_is_multi_sheet ---

def test_is_multi_sheet_minimal():
    assert ods_is_multi_sheet(MINIMAL) is False


def test_is_multi_sheet_numeric():
    assert ods_is_multi_sheet(NUMERIC) is False


def test_is_multi_sheet_single():
    assert ods_is_multi_sheet(SINGLE) is False


# --- ods_last_sheet_row_count ---

def test_last_sheet_row_count_minimal():
    assert ods_last_sheet_row_count(MINIMAL) == 2


def test_last_sheet_row_count_numeric():
    assert ods_last_sheet_row_count(NUMERIC) == 1


def test_last_sheet_row_count_single():
    result = ods_last_sheet_row_count(SINGLE)
    assert isinstance(result, int)
    assert result >= 0


# --- ods_has_text_cells ---

def test_has_text_cells_minimal():
    assert ods_has_text_cells(MINIMAL) is True


def test_has_text_cells_numeric():
    assert ods_has_text_cells(NUMERIC) is True


def test_has_text_cells_single():
    result = ods_has_text_cells(SINGLE)
    assert isinstance(result, bool)


# --- ods_sheet_names_list ---

def test_sheet_names_list_minimal():
    assert ods_sheet_names_list(MINIMAL) == ["Sheet1"]


def test_sheet_names_list_numeric():
    assert ods_sheet_names_list(NUMERIC) == ["Sheet1"]


def test_sheet_names_list_returns_list():
    result = ods_sheet_names_list(SINGLE)
    assert isinstance(result, list)
    assert len(result) >= 1
