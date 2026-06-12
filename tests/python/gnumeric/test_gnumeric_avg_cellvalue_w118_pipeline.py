"""
test_gnumeric_avg_cellvalue_w118_pipeline.py -- Gnumeric average_column + get_cell_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-118
Tests average_column returns float, correct average=40.0,
get_cell_value returns str, correct value at (0,0)="10", value at (1,1)="50".
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    average_column,
    get_cell_value,
)

_SHEETS = [{"name": "Data", "rows": [["10", "20", "30"], ["40", "50", "60"], ["70", "80", "90"]]}]


def test_average_column_returns_float():
    model = create_gnumeric(_SHEETS)
    result = average_column(model, 0, 0)
    assert isinstance(result, float)


def test_average_column_correct():
    model = create_gnumeric(_SHEETS)
    result = average_column(model, 0, 0)
    assert abs(result - 40.0) < 1e-9


def test_get_cell_value_returns_str():
    model = create_gnumeric(_SHEETS)
    result = get_cell_value(model, 0, 0, 0)
    assert isinstance(result, str)


def test_get_cell_value_correct():
    model = create_gnumeric(_SHEETS)
    result = get_cell_value(model, 0, 0, 0)
    assert result == "10"


def test_get_cell_value_middle():
    model = create_gnumeric(_SHEETS)
    result = get_cell_value(model, 0, 1, 1)
    assert result == "50"
