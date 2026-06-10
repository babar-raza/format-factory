"""Tests for gnumeric.gnumeric_codec.fill_row() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT / "src" / "python"))

from gnumeric.gnumeric_codec import create_gnumeric, fill_row


def test_fills_row_values():
    model = create_gnumeric([{"name": "Sheet1"}])
    result = fill_row(model, 0, 0, ["X", "Y", "Z"])
    grid = result["sheets"][0]["cell_grid"]
    assert grid[(0, 0)] == "X"
    assert grid[(0, 1)] == "Y"
    assert grid[(0, 2)] == "Z"


def test_fills_non_zero_row():
    model = create_gnumeric([{"name": "Sheet1"}])
    result = fill_row(model, 0, 2, ["A", "B"])
    grid = result["sheets"][0]["cell_grid"]
    assert grid[(2, 0)] == "A"
    assert grid[(2, 1)] == "B"


def test_does_not_mutate_original():
    model = create_gnumeric([{"name": "Sheet1"}])
    fill_row(model, 0, 0, ["X"])
    assert model["sheets"][0].get("cell_grid", {}) == {}


def test_out_of_range_returns_unchanged():
    model = create_gnumeric([{"name": "Sheet1"}])
    result = fill_row(model, 99, 0, ["X"])
    assert result is model


def test_returns_dict():
    model = create_gnumeric([{"name": "Sheet1"}])
    assert isinstance(fill_row(model, 0, 0, ["A"]), dict)
