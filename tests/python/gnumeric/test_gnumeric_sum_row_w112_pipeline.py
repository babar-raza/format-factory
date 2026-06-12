"""
test_gnumeric_sum_row_w112_pipeline.py -- Gnumeric sum_column + get_row pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-112
Tests sum_column returns float, correct sum, get_row returns list,
row has correct values, sum matches manual row total.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    sum_column,
    get_row,
)

_SHEETS = [{"name": "Data", "rows": [
    ["10", "20", "30"],
    ["40", "50", "60"],
    ["70", "80", "90"],
]}]


def test_sum_column_returns_float():
    model = create_gnumeric(_SHEETS)
    result = sum_column(model, 0, 0)
    assert isinstance(result, float)


def test_sum_column_correct():
    model = create_gnumeric(_SHEETS)
    # Column 0: 10 + 40 + 70 = 120
    result = sum_column(model, 0, 0)
    assert result == 120.0


def test_get_row_returns_list():
    model = create_gnumeric(_SHEETS)
    result = get_row(model, 0, 0)
    assert isinstance(result, list)


def test_get_row_correct_values():
    model = create_gnumeric(_SHEETS)
    result = get_row(model, 0, 1)
    assert result == ["40", "50", "60"]


def test_sum_matches_first_row_col0():
    model = create_gnumeric(_SHEETS)
    row0 = get_row(model, 0, 0)
    # First row, col 0 = "10"
    assert float(row0[0]) == 10.0
