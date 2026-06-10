"""Tests for gnumeric.gnumeric_codec.get_sheet_as_rows() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, get_sheet_as_rows


def _model():
    model = create_gnumeric([{"name": "Sheet1"}])
    sheets = list(model["sheets"])
    sheet = dict(sheets[0])
    sheet["cell_grid"] = {
        (0, 0): "A1", (0, 1): "B1",
        (1, 0): "A2", (1, 1): "B2",
    }
    sheets[0] = sheet
    return {**model, "sheets": sheets}


def test_returns_two_rows():
    rows = get_sheet_as_rows(_model(), 0)
    assert len(rows) == 2


def test_first_row_values():
    rows = get_sheet_as_rows(_model(), 0)
    assert rows[0] == ["A1", "B1"]


def test_second_row_values():
    rows = get_sheet_as_rows(_model(), 0)
    assert rows[1] == ["A2", "B2"]


def test_out_of_range_returns_empty():
    assert get_sheet_as_rows(_model(), 99) == []


def test_empty_sheet_returns_empty():
    model = create_gnumeric([{"name": "Sheet1"}])
    assert get_sheet_as_rows(model, 0) == []
