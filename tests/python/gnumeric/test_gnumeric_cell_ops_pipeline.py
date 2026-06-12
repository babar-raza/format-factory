"""
test_gnumeric_cell_ops_pipeline.py -- Gnumeric cell operations pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-47
Tests set_cell_value + read_cell, get_all_values list, fill_column then get_column,
count_nonempty_cells, clear_cell to empty.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    set_cell_value,
    read_cell,
    get_all_values,
    fill_column,
    get_column,
    count_nonempty_cells,
    clear_cell,
    get_cell_value,
)

_SHEETS = [{"name": "Sheet1", "rows": [["A", "B"], ["1", "2"], ["3", "4"]]}]


def _make_model():
    return create_gnumeric(_SHEETS)


def test_set_and_read_cell():
    model = _make_model()
    model = set_cell_value(model, 0, 0, 0, "Updated")
    val = read_cell(model, 0, 0, 0)
    assert val == "Updated"


def test_get_all_values_list():
    model = _make_model()
    vals = get_all_values(model, 0)
    assert isinstance(vals, list)
    assert "A" in vals


def test_fill_column_then_get():
    model = _make_model()
    model = fill_column(model, 0, 0, ["X", "Y", "Z"])
    col = get_column(model, 0, 0)
    assert col[0] == "X"
    assert col[1] == "Y"


def test_count_nonempty_cells():
    model = _make_model()
    count = count_nonempty_cells(model, 0)
    assert count == 6  # 3 rows x 2 cols


def test_clear_cell_to_empty():
    model = _make_model()
    model = clear_cell(model, 0, 0, 0)
    val = get_cell_value(model, 0, 0, 0)
    assert val == ""
