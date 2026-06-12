"""
test_gnumeric_write_reload_roundtrip.py -- Gnumeric write and reload roundtrip tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-18
Tests that Gnumeric mutations (set_cell_value, create_gnumeric) persist
after write_gnumeric + reload.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    load,
    set_cell_value,
    write_gnumeric,
    get_cell_value,
    create_gnumeric,
    get_row_count,
    get_column_count,
)


def test_set_cell_value_persists_after_reload(tmp_path):
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    m2 = set_cell_value(m, 0, 0, 0, "CHANGED")
    dest = tmp_path / "out.gnumeric"
    write_gnumeric(m2, str(dest))
    m3 = load(str(dest))
    assert get_cell_value(m3, 0, 0, 0) == "CHANGED"


def test_other_cells_unchanged_after_reload(tmp_path):
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    m2 = set_cell_value(m, 0, 0, 0, "CHANGED")
    dest = tmp_path / "out.gnumeric"
    write_gnumeric(m2, str(dest))
    m3 = load(str(dest))
    # Other cells should remain
    assert get_cell_value(m3, 0, 0, 1) == "Score"


def test_create_and_write_reload(tmp_path):
    m = create_gnumeric([{
        "name": "Sheet1",
        "rows": [["Hello"], ["World"]],
    }])
    dest = tmp_path / "created.gnumeric"
    write_gnumeric(m, str(dest))
    m2 = load(str(dest))
    assert get_cell_value(m2, 0, 0, 0) == "Hello"


def test_create_write_reload_row_count(tmp_path):
    m = create_gnumeric([{
        "name": "Sheet1",
        "rows": [["A"], ["B"], ["C"]],
    }])
    dest = tmp_path / "three_rows.gnumeric"
    write_gnumeric(m, str(dest))
    m2 = load(str(dest))
    assert get_row_count(m2, 0) == 3


def test_multiple_set_cells_persist(tmp_path):
    m = load(str(_SAMPLES / "multi-cell-basic.gnumeric"))
    m2 = set_cell_value(m, 0, 0, 0, "X")
    m3 = set_cell_value(m2, 0, 0, 1, "Y")
    dest = tmp_path / "out.gnumeric"
    write_gnumeric(m3, str(dest))
    m4 = load(str(dest))
    assert get_cell_value(m4, 0, 0, 0) == "X"
    assert get_cell_value(m4, 0, 0, 1) == "Y"
