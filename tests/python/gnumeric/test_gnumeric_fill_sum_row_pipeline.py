"""
test_gnumeric_fill_sum_row_pipeline.py -- Gnumeric fill_row + sum_row pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-83
Tests fill_row updates values, sum_row float, sum_row correct value,
fill_row returns model dict, get_row after fill_row matches values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    fill_row,
    sum_row,
    get_row,
)

_SHEETS = [
    {
        "name": "Nums",
        "rows": [
            ["10", "20", "30"],
            ["5", "15", "25"],
        ],
    }
]


def test_fill_row_updates_values(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 0, ["100", "200", "300"])
    row = get_row(model, 0, 0)
    assert row[0] == "100"
    assert row[1] == "200"


def test_sum_row_float(tmp_path):
    model = create_gnumeric(_SHEETS)
    total = sum_row(model, 0, 0)
    assert isinstance(total, float)


def test_sum_row_correct_value(tmp_path):
    model = create_gnumeric(_SHEETS)
    total = sum_row(model, 0, 0)
    assert total == 60.0


def test_fill_row_returns_model_dict(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = fill_row(model, 0, 1, ["1", "2", "3"])
    assert isinstance(result, dict)


def test_get_row_after_fill_matches(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = fill_row(model, 0, 1, ["7", "8", "9"])
    row = get_row(model, 0, 1)
    assert row[0] == "7"
    assert row[2] == "9"
