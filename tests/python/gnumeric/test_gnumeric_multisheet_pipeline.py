"""
test_gnumeric_multisheet_pipeline.py -- Gnumeric multi-sheet copy/delete pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-44
Tests copy_sheet increases count, delete_sheet decreases count,
get_sheet_by_name finds sheet, add_sheet then rename, get_sheet_index for added sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    write_gnumeric,
    copy_sheet,
    delete_sheet,
    get_sheet_by_name,
    add_sheet,
    rename_sheet,
    get_sheet_index,
    get_sheet_count,
    get_sheet_names,
)

_SHEETS = [
    {"name": "Alpha", "rows": [["x", "y"], ["1", "2"]]},
    {"name": "Beta", "rows": [["a", "b"], ["3", "4"]]},
]
_MODEL = create_gnumeric(_SHEETS)


def test_copy_sheet_increases_count():
    model = create_gnumeric(_SHEETS)
    model = copy_sheet(model, 0)
    assert model["sheet_count"] == 3


def test_delete_sheet_decreases_count():
    model = create_gnumeric(_SHEETS)
    model = delete_sheet(model, 1)
    assert model["sheet_count"] == 1


def test_get_sheet_by_name_finds_beta():
    model = create_gnumeric(_SHEETS)
    sheet = get_sheet_by_name(model, "Beta")
    assert sheet is not None
    assert sheet["name"] == "Beta"


def test_add_then_rename_sheet():
    model = create_gnumeric(_SHEETS)
    model = add_sheet(model, "Gamma")
    model = rename_sheet(model, 2, "Delta")
    names = get_sheet_names(None) if False else [s["name"] for s in model["sheets"]]
    assert "Delta" in names


def test_get_sheet_index_for_beta():
    model = create_gnumeric(_SHEETS)
    idx = get_sheet_index(model, "Beta")
    assert idx == 1
