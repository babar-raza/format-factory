"""
test_gnumeric_clear_cell_count_pipeline.py -- Gnumeric clear_cell + count_nonempty_cells pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-86
Tests count_nonempty_cells int, clear_cell decreases count, clear_cell returns model,
count_nonempty_cells after clear, clear_cell value becomes empty.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    clear_cell,
    count_nonempty_cells,
    get_cell_value,
)

_SHEETS = [
    {
        "name": "Data",
        "rows": [
            ["A", "B", "C"],
            ["1", "2", "3"],
        ],
    }
]


def test_count_nonempty_cells_int(tmp_path):
    model = create_gnumeric(_SHEETS)
    count = count_nonempty_cells(model, 0)
    assert isinstance(count, int)
    assert count == 6


def test_clear_cell_decreases_count(tmp_path):
    model = create_gnumeric(_SHEETS)
    before = count_nonempty_cells(model, 0)
    model = clear_cell(model, 0, 0, 0)
    after = count_nonempty_cells(model, 0)
    assert after == before - 1


def test_clear_cell_returns_model(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = clear_cell(model, 0, 1, 1)
    assert isinstance(result, dict)


def test_count_nonempty_cells_after_clear(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = clear_cell(model, 0, 0, 0)
    model = clear_cell(model, 0, 0, 1)
    count = count_nonempty_cells(model, 0)
    assert count == 4


def test_clear_cell_value_becomes_empty(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = clear_cell(model, 0, 0, 0)
    val = get_cell_value(model, 0, 0, 0)
    assert val == "" or val is None
