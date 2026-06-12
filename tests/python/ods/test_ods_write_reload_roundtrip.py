"""
test_ods_write_reload_roundtrip.py -- ODS write and reload roundtrip tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-17
Tests that ODS mutations (set_cell_value, add_row, rename_sheet) are preserved
after write_ods + parse_ods_strict reload.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

_SAMPLES = _REPO / "samples" / "by-format" / "ods" / "valid"

from ods.ods_parser import parse_ods_strict, get_cell_value
from ods.ods_writer import set_cell_value, add_row, rename_sheet, write_ods, document_to_ods_bytes


def test_set_cell_and_reload(tmp_path):
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    set_cell_value(doc, 0, 0, 0, "MODIFIED")
    dest = tmp_path / "out.ods"
    write_ods(doc, str(dest))
    val = get_cell_value(str(dest), 0, 0, 0)
    assert val == "MODIFIED"


def test_add_row_and_reload(tmp_path):
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    before_count = len(doc.sheets[0].rows)
    add_row(doc, 0, ["New", "99"])
    dest = tmp_path / "out.ods"
    write_ods(doc, str(dest))
    doc2 = parse_ods_strict(str(dest))
    assert len(doc2.sheets[0].rows) == before_count + 1


def test_rename_sheet_and_reload(tmp_path):
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    original_name = doc.sheets[0].name
    rename_sheet(doc, original_name, "NewName")
    dest = tmp_path / "out.ods"
    write_ods(doc, str(dest))
    doc2 = parse_ods_strict(str(dest))
    assert doc2.sheets[0].name == "NewName"


def test_document_to_ods_bytes_is_bytes():
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    bts = document_to_ods_bytes(doc)
    assert isinstance(bts, bytes)
    assert len(bts) > 0


def test_multiple_mutations_persist(tmp_path):
    doc = parse_ods_strict(str(_SAMPLES / "minimal-spreadsheet.ods"))
    set_cell_value(doc, 0, 0, 0, "Header1")
    set_cell_value(doc, 0, 0, 1, "Header2")
    dest = tmp_path / "out.ods"
    write_ods(doc, str(dest))
    assert get_cell_value(str(dest), 0, 0, 0) == "Header1"
    assert get_cell_value(str(dest), 0, 0, 1) == "Header2"
