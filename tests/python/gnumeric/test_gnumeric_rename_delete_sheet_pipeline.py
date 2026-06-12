"""
test_gnumeric_rename_delete_sheet_pipeline.py -- Gnumeric rename_sheet + delete_sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-89
Tests rename_sheet changes name, rename_sheet returns model, delete_sheet decreases count,
delete_sheet returns model, sheet count after operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric import (
    create_gnumeric,
    rename_sheet,
    delete_sheet,
    sheet_names,
)

_SHEETS = [
    {"name": "First", "rows": [["A", "B"]]},
    {"name": "Second", "rows": [["C", "D"]]},
    {"name": "Third", "rows": [["E", "F"]]},
]


def test_rename_sheet_changes_name(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = rename_sheet(model, 0, "NewFirst")
    names = sheet_names(model)
    assert "NewFirst" in names
    assert "First" not in names


def test_rename_sheet_returns_model(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = rename_sheet(model, 1, "RenamedSecond")
    assert isinstance(result, dict)


def test_delete_sheet_decreases_count(tmp_path):
    model = create_gnumeric(_SHEETS)
    before = len(model["sheets"])
    model = delete_sheet(model, 2)
    assert len(model["sheets"]) == before - 1


def test_delete_sheet_returns_model(tmp_path):
    model = create_gnumeric(_SHEETS)
    result = delete_sheet(model, 0)
    assert isinstance(result, dict)


def test_sheet_count_after_operations(tmp_path):
    model = create_gnumeric(_SHEETS)
    model = rename_sheet(model, 0, "X")
    model = delete_sheet(model, 1)
    assert len(model["sheets"]) == 2
    assert "X" in sheet_names(model)
