"""
test_gnumeric_fill_row_pipeline.py -- Gnumeric fill_row pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-59
Tests fill_row returns model, fill_row values readable, get_row_values list,
fill_row + sum_row, row_count after fill.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    fill_row,
    get_row_values,
    sum_row,
    row_count,
)

_SHEETS = [{"name": "Sheet1", "rows": []}]


def test_fill_row_returns_model():
    model = create_gnumeric(_SHEETS)
    result = fill_row(model, 0, 0, ["10", "20", "30"])
    assert isinstance(result, dict)


def test_fill_row_values_readable():
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 0, ["10", "20", "30"])
    vals = get_row_values(model, 0, 0)
    assert vals == ["10", "20", "30"]


def test_get_row_values_list():
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 1, ["A", "B"])
    vals = get_row_values(model, 0, 1)
    assert isinstance(vals, list)
    assert "A" in vals


def test_fill_row_and_sum_row():
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 0, ["5", "10", "15"])
    total = sum_row(model, 0, 0)
    assert total == 30.0


def test_row_count_after_fill():
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 2, ["X", "Y"])
    count = row_count(model, 0)
    assert count == 3
