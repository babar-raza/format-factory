"""
test_gnumeric_conveyor_deepening.py -- Gnumeric product deepening tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-5
Tests export, create, write, and sheet management functions for Gnumeric.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "gnumeric"

from gnumeric.gnumeric_codec import (
    load,
    create_gnumeric,
    write_gnumeric,
    export_to_csv,
    export_to_json,
    probe_gnumeric,
    get_sheet_names,
    get_cell_value,
    set_cell_value,
    get_row,
    get_column,
    add_sheet,
    delete_sheet,
    rename_sheet,
    copy_sheet,
)


def test_export_to_csv():
    csv_str = export_to_csv(_SAMPLES / "multi-cell-basic.gnumeric")
    assert isinstance(csv_str, str)
    assert len(csv_str) > 0


def test_export_to_json():
    json_str = export_to_json(_SAMPLES / "multi-cell-basic.gnumeric")
    assert isinstance(json_str, str)
    assert len(json_str) > 0


def test_probe_gnumeric():
    assert probe_gnumeric(_SAMPLES / "minimal-spreadsheet.gnumeric") is True


def test_get_sheet_names():
    names = get_sheet_names(_SAMPLES / "minimal-spreadsheet.gnumeric")
    assert isinstance(names, list)
    assert len(names) >= 1


def test_create_and_write_roundtrip(tmp_path):
    model = create_gnumeric([
        {"name": "Sheet1", "cells": [{"row": 0, "col": 0, "value": "test"}]}
    ])
    out = tmp_path / "created.gnumeric"
    write_gnumeric(model, str(out))
    reloaded = load(out)
    assert reloaded["sheet_count"] == 1


def test_get_cell_value():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    val = get_cell_value(model, 0, 0, 0)
    assert val is not None


def test_set_cell_value(tmp_path):
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    updated = set_cell_value(model, 0, 0, 0, "new_value")
    val = get_cell_value(updated, 0, 0, 0)
    assert val == "new_value"


def test_get_row():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    row = get_row(model, 0, 0)
    assert isinstance(row, list)


def test_get_column():
    model = load(_SAMPLES / "multi-cell-basic.gnumeric")
    col = get_column(model, 0, 0)
    assert isinstance(col, list)


def test_add_and_delete_sheet():
    model = load(_SAMPLES / "minimal-spreadsheet.gnumeric")
    original_count = model["sheet_count"]
    model = add_sheet(model, "NewSheet")
    assert model["sheet_count"] == original_count + 1
    model = delete_sheet(model, model["sheet_count"] - 1)
    assert model["sheet_count"] == original_count


def test_rename_sheet():
    model = load(_SAMPLES / "minimal-spreadsheet.gnumeric")
    model = rename_sheet(model, 0, "Renamed")
    names = [s["name"] for s in model["sheets"]]
    assert "Renamed" in names


def test_copy_sheet():
    model = load(_SAMPLES / "minimal-spreadsheet.gnumeric")
    original_count = model["sheet_count"]
    model = copy_sheet(model, 0)
    assert model["sheet_count"] == original_count + 1
