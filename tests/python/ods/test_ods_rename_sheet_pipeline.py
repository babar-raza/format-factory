"""
test_ods_rename_sheet_pipeline.py -- ODS rename sheet + add/remove sheet pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-41
Tests rename_sheet success, renamed sheet visible in get_sheet_names,
add_sheet increases count, remove_sheet decreases count, roundtrip after rename.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods import (
    OdsDocument,
    OdsSheet,
    OdsRow,
    OdsCell,
    write_ods,
    rename_sheet,
    add_sheet,
    remove_sheet,
    get_sheet_names,
    count_sheets,
    parse_ods_strict,
)


def _make_doc():
    sheet = OdsSheet(name="Original")
    sheet.rows.append(OdsRow(cells=[OdsCell(value="Hello"), OdsCell(value="World")]))
    return OdsDocument(sheets=[sheet])


def test_rename_sheet_success():
    doc = _make_doc()
    ok, msg = rename_sheet(doc, "Original", "Renamed")
    assert ok is True
    assert doc.sheets[0].name == "Renamed"


def test_renamed_sheet_in_get_sheet_names(tmp_path):
    doc = _make_doc()
    rename_sheet(doc, "Original", "Renamed")
    dest = tmp_path / "renamed.ods"
    write_ods(doc, str(dest))
    names = get_sheet_names(str(dest))
    assert "Renamed" in names
    assert "Original" not in names


def test_add_sheet_increases_count(tmp_path):
    doc = _make_doc()
    add_sheet(doc, "Extra")
    dest = tmp_path / "added.ods"
    write_ods(doc, str(dest))
    assert count_sheets(str(dest)) == 2


def test_remove_sheet_decreases_count(tmp_path):
    doc = _make_doc()
    add_sheet(doc, "ToRemove")
    remove_sheet(doc, "ToRemove")
    dest = tmp_path / "removed.ods"
    write_ods(doc, str(dest))
    assert count_sheets(str(dest)) == 1


def test_roundtrip_after_rename(tmp_path):
    doc = _make_doc()
    rename_sheet(doc, "Original", "FinalName")
    dest = tmp_path / "roundtrip.ods"
    write_ods(doc, str(dest))
    reloaded = parse_ods_strict(str(dest))
    assert reloaded.sheets[0].name == "FinalName"
