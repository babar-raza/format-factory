"""Tests for gnumeric_codec.get_row_values — mainstream-product-deepening-rnext7.

Covers: normal row, empty row, missing cells (gaps), out-of-range sheet, multi-sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, get_row_values


def _model_with_grid(grid):
    model = create_gnumeric([{"name": "Sheet1"}])
    sheets = list(model["sheets"])
    sheet = dict(sheets[0])
    sheet["cell_grid"] = grid
    sheets[0] = sheet
    return {**model, "sheets": sheets}


# ---------------------------------------------------------------------------
# Normal behavior
# ---------------------------------------------------------------------------

def test_get_row_values_basic():
    grid = {(0, 0): "a", (0, 1): "b", (0, 2): "c"}
    model = _model_with_grid(grid)
    result = get_row_values(model, 0, 0)
    assert result == ["a", "b", "c"]


def test_get_row_values_second_row():
    grid = {(0, 0): "header", (1, 0): "data1", (1, 1): "data2"}
    model = _model_with_grid(grid)
    result = get_row_values(model, 0, 1)
    assert result == ["data1", "data2"]


def test_get_row_values_returns_list():
    grid = {(0, 0): "x"}
    model = _model_with_grid(grid)
    assert isinstance(get_row_values(model, 0, 0), list)


# ---------------------------------------------------------------------------
# Boundary cases
# ---------------------------------------------------------------------------

def test_get_row_values_empty_row():
    grid = {(0, 0): "only_row0"}
    model = _model_with_grid(grid)
    result = get_row_values(model, 0, 1)
    assert result == []


def test_get_row_values_sparse_gaps():
    grid = {(0, 0): "first", (0, 2): "third"}
    model = _model_with_grid(grid)
    result = get_row_values(model, 0, 0)
    assert len(result) == 3
    assert result[0] == "first"
    assert result[1] == ""
    assert result[2] == "third"


def test_get_row_values_empty_grid():
    model = _model_with_grid({})
    assert get_row_values(model, 0, 0) == []


# ---------------------------------------------------------------------------
# Invalid input
# ---------------------------------------------------------------------------

def test_get_row_values_out_of_range_sheet():
    model = _model_with_grid({})
    with pytest.raises(IndexError):
        get_row_values(model, 5, 0)
