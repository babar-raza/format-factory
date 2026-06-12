"""
test_gnumeric_sum_avg_col_pipeline.py -- Gnumeric sum_column + average_column pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-101
Tests sum_column float, sum=60.0, average_column float, average=20.0,
sum of col1 (different values) correct.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    sum_column,
    average_column,
)

_SHEETS = [
    {
        "name": "Data",
        "rows": [
            ["10", "100"],
            ["20", "200"],
            ["30", "300"],
        ],
    }
]


def test_sum_column_returns_float():
    model = create_gnumeric(_SHEETS)
    total = sum_column(model, 0, 0)
    assert isinstance(total, float)


def test_sum_column_correct_value():
    model = create_gnumeric(_SHEETS)
    total = sum_column(model, 0, 0)
    assert total == 60.0


def test_sum_column_second_col():
    model = create_gnumeric(_SHEETS)
    total = sum_column(model, 0, 1)
    assert total == 600.0


def test_average_column_returns_float():
    model = create_gnumeric(_SHEETS)
    avg = average_column(model, 0, 0)
    assert isinstance(avg, float)


def test_average_column_correct_value():
    model = create_gnumeric(_SHEETS)
    avg = average_column(model, 0, 0)
    assert avg == 20.0
