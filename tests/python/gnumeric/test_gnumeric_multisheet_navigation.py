"""
test_gnumeric_multisheet_navigation.py -- Gnumeric multi-sheet creation and navigation.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-23
Tests add_sheet, get_sheet_by_name, copy_sheet, sheet_names with
write_gnumeric+reload roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from gnumeric.gnumeric_codec import (
    create_gnumeric,
    add_sheet,
    get_sheet_by_name,
    copy_sheet,
    sheet_names,
    get_row_count,
    get_cell_value,
    write_gnumeric,
    load,
)


def test_add_sheet_increases_count():
    m = create_gnumeric([{"name": "Sheet1", "rows": [["A"]]}])
    m2 = add_sheet(m, "Sheet2")
    assert len(sheet_names(m2)) == 2


def test_add_sheet_name_in_list():
    m = create_gnumeric([{"name": "Sheet1", "rows": [["A"]]}])
    m2 = add_sheet(m, "ExtraSheet")
    assert "ExtraSheet" in sheet_names(m2)


def test_get_sheet_by_name_returns_sheet():
    m = create_gnumeric([{"name": "Data", "rows": [["Hello"]]}])
    sheet = get_sheet_by_name(m, "Data")
    assert sheet is not None
    assert sheet.get("name") == "Data"


def test_copy_sheet_increases_count():
    m = create_gnumeric([{"name": "Original", "rows": [["X"], ["Y"]]}])
    m2 = copy_sheet(m, 0)
    assert len(sheet_names(m2)) == 2


def test_add_sheet_write_reload_persists(tmp_path):
    m = create_gnumeric([{"name": "Main", "rows": [["Data"]]}])
    m2 = add_sheet(m, "Summary")
    dest = tmp_path / "multisheet.gnumeric"
    write_gnumeric(m2, str(dest))
    m3 = load(str(dest))
    names = sheet_names(m3)
    assert "Main" in names
    assert "Summary" in names
