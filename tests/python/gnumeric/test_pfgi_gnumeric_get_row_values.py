"""Tests for gnumeric.gnumeric_codec.get_row_values() — PFGI Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, set_cell_value, get_row_values


def _make_model_with_data():
    model = create_gnumeric([{"name": "Sheet1"}])
    model = set_cell_value(model, 0, 0, 0, "A1")
    model = set_cell_value(model, 0, 0, 1, "B1")
    model = set_cell_value(model, 0, 0, 2, "C1")
    model = set_cell_value(model, 0, 1, 0, "A2")
    model = set_cell_value(model, 0, 1, 1, "B2")
    return model


def test_first_row_returns_all_values():
    model = _make_model_with_data()
    row = get_row_values(model, 0, 0)
    assert row == ["A1", "B1", "C1"]


def test_second_row_values():
    model = _make_model_with_data()
    row = get_row_values(model, 0, 1)
    assert row == ["A2", "B2"]


def test_empty_row_returns_empty_list():
    model = _make_model_with_data()
    # Row 5 has no data
    row = get_row_values(model, 0, 5)
    assert row == []


def test_out_of_range_sheet_raises():
    model = create_gnumeric([{"name": "Sheet1"}])
    with pytest.raises(IndexError):
        get_row_values(model, 99, 0)


def test_negative_sheet_raises():
    model = create_gnumeric([{"name": "Sheet1"}])
    with pytest.raises(IndexError):
        get_row_values(model, -1, 0)


def test_returns_list():
    model = _make_model_with_data()
    assert isinstance(get_row_values(model, 0, 0), list)


def test_single_cell_row():
    model = create_gnumeric([{"name": "S"}])
    model = set_cell_value(model, 0, 2, 0, "only")
    row = get_row_values(model, 0, 2)
    assert row == ["only"]


def test_sparse_row_fills_empty_strings():
    model = create_gnumeric([{"name": "S"}])
    # col 0 empty, col 2 has value
    model = set_cell_value(model, 0, 0, 2, "C")
    row = get_row_values(model, 0, 0)
    # Expect ["", "", "C"]
    assert len(row) == 3
    assert row[2] == "C"
    assert row[0] == ""
