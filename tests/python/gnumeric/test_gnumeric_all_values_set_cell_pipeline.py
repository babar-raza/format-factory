"""
test_gnumeric_all_values_set_cell_pipeline.py -- Gnumeric get_all_values + set_cell_value pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-92
Tests get_all_values returns list, set_cell_value returns model, set_cell_value updates value,
get_all_values after set includes new value, set then get_cell_value matches.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    get_all_values,
    set_cell_value,
    get_cell_value,
)

_SHEETS = [
    {
        "name": "Grid",
        "rows": [
            ["A", "B", "C"],
            ["1", "2", "3"],
        ],
    }
]


def test_get_all_values_returns_list(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = get_all_values(model, 0)
    assert isinstance(result, list)


def test_set_cell_value_returns_model(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = set_cell_value(model, 0, 0, 0, "X")
    assert isinstance(result, dict)


def test_set_cell_value_updates_value(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = set_cell_value(model, 0, 0, 0, "Updated")
    val = get_cell_value(model, 0, 0, 0)
    assert val == "Updated"


def test_get_all_values_after_set(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = set_cell_value(model, 0, 0, 0, "NewVal")
    values = get_all_values(model, 0)
    assert "NewVal" in values


def test_set_then_get_cell_matches(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = set_cell_value(model, 0, 1, 2, "999")
    val = get_cell_value(model, 0, 1, 2)
    assert val == "999"
