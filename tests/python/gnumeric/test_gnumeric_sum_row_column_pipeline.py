"""
test_gnumeric_sum_row_column_pipeline.py -- Gnumeric sum_row + sum_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-53
Tests sum_row returns float, sum_row correct value, sum_row skips text,
sum_column correct value, sum_column after fill_column.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    set_cell_value,
    sum_row,
    sum_column,
    fill_column,
)

# Row 0: 10, 20, 30  (sum=60)
# Row 1: 5, "skip", 15  (sum=20)
# Row 2: 100, "", ""  (col 0 sum = 10+5+100=115)
_SHEETS = [{"name": "Sheet1", "rows": [
    ["10", "20", "30"],
    ["5", "skip", "15"],
    ["100", "", ""],
]}]


def test_sum_row_returns_float():
    model = create_gnumeric(_SHEETS)
    result = sum_row(model, 0, 0)
    assert isinstance(result, float)


def test_sum_row_correct_value():
    model = create_gnumeric(_SHEETS)
    result = sum_row(model, 0, 0)
    assert result == 60.0


def test_sum_row_skips_text():
    model = create_gnumeric(_SHEETS)
    result = sum_row(model, 0, 1)
    assert result == 20.0


def test_sum_column_correct_value():
    model = create_gnumeric(_SHEETS)
    result = sum_column(model, 0, 0)
    assert result == 115.0


def test_sum_column_after_fill():
    model = create_gnumeric([{"name": "Sheet1", "rows": []}])
    model = fill_column(model, 0, 0, ["7", "8", "9"])
    result = sum_column(model, 0, 0)
    assert result == 24.0
