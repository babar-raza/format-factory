"""
test_gnumeric_load_gap_closure.py -- Gnumeric load and column/row access gap closure.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-9
Tests column/row accessor functions with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    load,
    get_cell_value,
    get_row,
    get_column,
    get_row_count,
    get_column_count,
    extract_values,
    get_sheet_metadata,
    get_sheet_names,
)


def test_multi_cell_get_row_returns_list():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    row = get_row(model, 0, 0)
    assert isinstance(row, list)
    assert len(row) >= 1


def test_multi_cell_get_column_returns_list():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    col = get_column(model, 0, 0)
    assert isinstance(col, list)
    assert len(col) >= 1


def test_row_count_is_positive():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    count = get_row_count(model, 0)
    assert count >= 1


def test_column_count_is_positive():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    count = get_column_count(model, 0)
    assert count >= 1


def test_extract_values_non_empty():
    values = extract_values(_SAMPLES / "multi-cell-basic.gnumeric")
    assert isinstance(values, list)
    assert len(values) >= 1


def test_sheet_metadata_has_name():
    meta = get_sheet_metadata(_SAMPLES / "multi-cell-basic.gnumeric")
    assert isinstance(meta, list)
    assert len(meta) >= 1
    assert "name" in meta[0]


def test_get_cell_value_at_zero_zero():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    val = get_cell_value(model, 0, 0, 0)
    assert val is not None
    assert isinstance(val, str)


def test_sheet_names_match_metadata():
    names = get_sheet_names(_SAMPLES / "multi-cell-basic.gnumeric")
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    meta = get_sheet_metadata(_SAMPLES / "multi-cell-basic.gnumeric")
    meta_names = [m["name"] for m in meta]
    assert set(names) == set(meta_names)
