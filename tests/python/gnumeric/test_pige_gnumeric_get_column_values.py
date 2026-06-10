"""Tests for gnumeric.gnumeric_codec.get_column_values() — PIGE Sprint."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, set_cell_value, get_column_values


def _make_model():
    model = create_gnumeric([{"name": "Sheet1"}])
    model = set_cell_value(model, 0, 0, 0, "A1")
    model = set_cell_value(model, 0, 1, 0, "A2")
    model = set_cell_value(model, 0, 2, 0, "A3")
    model = set_cell_value(model, 0, 0, 1, "B1")
    model = set_cell_value(model, 0, 1, 1, "B2")
    return model


def test_first_column_returns_all_values():
    model = _make_model()
    col = get_column_values(model, 0, 0)
    assert col == ["A1", "A2", "A3"]


def test_second_column_values():
    model = _make_model()
    col = get_column_values(model, 0, 1)
    assert col == ["B1", "B2"]


def test_empty_column_returns_empty_list():
    model = _make_model()
    col = get_column_values(model, 0, 5)
    assert col == []


def test_out_of_range_sheet_raises():
    model = create_gnumeric([{"name": "Sheet1"}])
    with pytest.raises(IndexError):
        get_column_values(model, 99, 0)


def test_negative_sheet_raises():
    model = create_gnumeric([{"name": "Sheet1"}])
    with pytest.raises(IndexError):
        get_column_values(model, -1, 0)


def test_returns_list():
    model = _make_model()
    assert isinstance(get_column_values(model, 0, 0), list)


def test_sparse_column_fills_empty_strings():
    model = create_gnumeric([{"name": "S"}])
    model = set_cell_value(model, 0, 2, 0, "only")
    col = get_column_values(model, 0, 0)
    assert len(col) == 3
    assert col[0] == ""
    assert col[2] == "only"


def test_available_from_package():
    from gnumeric import get_column_values as fn
    assert callable(fn)
