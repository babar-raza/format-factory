"""
test_gnumeric_set_cell_pipeline.py -- Gnumeric set_cell_value + nonempty cell pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-38
Tests set_cell_value mutates cell, count_nonempty_cells, clear_cell,
read_cell after set, get_all_values list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    set_cell_value,
    count_nonempty_cells,
    clear_cell,
    read_cell,
    get_all_values,
    get_cell_value,
)

_MODEL = create_gnumeric([{
    "name": "Sheet1",
    "rows": [["A", "B"], ["C", "D"]],
}])


def test_set_cell_value_mutates():
    m2 = set_cell_value(_MODEL, 0, 0, 0, "X")
    assert get_cell_value(m2, 0, 0, 0) == "X"


def test_count_nonempty_cells():
    count = count_nonempty_cells(_MODEL, 0)
    assert count == 4


def test_clear_cell_removes_value():
    m2 = clear_cell(_MODEL, 0, 0, 0)
    assert get_cell_value(m2, 0, 0, 0) == ""


def test_read_cell_after_set():
    m2 = set_cell_value(_MODEL, 0, 1, 1, "Z")
    val = read_cell(m2, 0, 1, 1)
    assert val == "Z"


def test_get_all_values_list():
    vals = get_all_values(_MODEL, 0)
    assert isinstance(vals, list)
    assert "A" in vals
    assert "D" in vals
