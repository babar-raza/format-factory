"""
test_gnumeric_add_delete_sheet_pipeline.py -- Gnumeric add/delete sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-68
Tests add_sheet increases count, delete_sheet decreases count, copy_sheet increases count,
add_sheet name exists, delete then add.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    add_sheet,
    delete_sheet,
    copy_sheet,
    sheet_names,
)

_SHEETS = [{"name": "Sheet1"}, {"name": "Sheet2"}]


def test_add_sheet_increases_count():
    model = create_gnumeric(_SHEETS)
    model = add_sheet(model, "Sheet3")
    assert len(sheet_names(model)) == 3


def test_delete_sheet_decreases_count():
    model = create_gnumeric(_SHEETS)
    model = delete_sheet(model, 0)
    assert len(sheet_names(model)) == 1


def test_copy_sheet_increases_count():
    model = create_gnumeric(_SHEETS)
    model = copy_sheet(model, 0)
    assert len(sheet_names(model)) == 3


def test_add_sheet_name_exists():
    model = create_gnumeric(_SHEETS)
    model = add_sheet(model, "NewSheet")
    assert "NewSheet" in sheet_names(model)


def test_delete_then_add():
    model = create_gnumeric(_SHEETS)
    model = delete_sheet(model, 0)
    model = add_sheet(model, "Replacement")
    names = sheet_names(model)
    assert len(names) == 2
    assert "Replacement" in names
