"""Tests for gnumeric.gnumeric_codec.row_count() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, row_count


def _model_with_grid(grid):
    model = create_gnumeric([{"name": "Sheet1"}])
    sheets = list(model["sheets"])
    sheet = dict(sheets[0])
    sheet["cell_grid"] = grid
    sheets[0] = sheet
    return {**model, "sheets": sheets}


def test_two_rows():
    grid = {(0, 0): "A", (1, 0): "B"}
    assert row_count(_model_with_grid(grid), 0) == 2


def test_single_row():
    assert row_count(_model_with_grid({(0, 0): "A", (0, 1): "B"}), 0) == 1


def test_empty_sheet():
    assert row_count(create_gnumeric([{"name": "S"}]), 0) == 0


def test_out_of_range():
    model = create_gnumeric([{"name": "S"}])
    assert row_count(model, 99) == 0


def test_returns_int():
    assert isinstance(row_count(create_gnumeric([{"name": "S"}]), 0), int)
