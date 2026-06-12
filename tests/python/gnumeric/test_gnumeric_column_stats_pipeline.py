"""
test_gnumeric_column_stats_pipeline.py -- Gnumeric column stats pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-71
Tests get_column_values returns list, column length, sum_column float,
get_column_count int, fill_column then get_column_values updated.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    get_column_values,
    sum_column,
    get_column_count,
    fill_column,
)


_SHEETS = [
    {
        "name": "Data",
        "rows": [
            ["10", "Alpha"],
            ["20", "Beta"],
            ["30", "Gamma"],
        ],
    }
]


def test_get_column_values_returns_list():
    model = create_gnumeric(_SHEETS)
    result = get_column_values(model, 0, 0)
    assert isinstance(result, list)


def test_get_column_values_length():
    model = create_gnumeric(_SHEETS)
    result = get_column_values(model, 0, 0)
    assert len(result) == 3


def test_sum_column_float():
    model = create_gnumeric(_SHEETS)
    total = sum_column(model, 0, 0)
    assert isinstance(total, float)
    assert total == 60.0


def test_get_column_count_int():
    model = create_gnumeric(_SHEETS)
    count = get_column_count(model, 0)
    assert isinstance(count, int)
    assert count == 2


def test_fill_column_then_get_values():
    model = create_gnumeric(_SHEETS)
    model = fill_column(model, 0, 0, ["5", "15", "25"])
    result = get_column_values(model, 0, 0)
    assert result[0] == "5"
    assert result[1] == "15"
    assert result[2] == "25"
