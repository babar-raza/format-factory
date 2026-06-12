"""
test_r157_ods_writer_ops.py — Tests for ODS writer mutation operations.

Tests set_cell_value, add_sheet, remove_sheet, rename_sheet.
"""
from __future__ import annotations

import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent))
from src.python.ods.ods_parser import OdsCell, OdsDocument, OdsRow, OdsSheet, parse_ods_strict
from src.python.ods.ods_writer import add_sheet, remove_sheet, rename_sheet, set_cell_value, write_ods


def _make_doc() -> OdsDocument:
    rows = [
        OdsRow(cells=[OdsCell(text="A1"), OdsCell(text="B1")]),
        OdsRow(cells=[OdsCell(text="A2"), OdsCell(text="B2")]),
    ]
    return OdsDocument(sheets=[OdsSheet(name="Data", rows=rows)])


class TestSetCellValue:
    def test_set_existing_cell(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 0, 0, 0, "New", "string")
        assert ok is True
        assert doc.sheets[0].rows[0].cells[0].text == "New"

    def test_set_extends_rows(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 0, 5, 0, "Deep", "string")
        assert ok is True
        assert len(doc.sheets[0].rows) == 6
        assert doc.sheets[0].rows[5].cells[0].text == "Deep"

    def test_set_extends_columns(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 0, 0, 5, "Wide", "string")
        assert ok is True
        assert len(doc.sheets[0].rows[0].cells) == 6

    def test_set_invalid_sheet_index(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 9, 0, 0, "X", "string")
        assert ok is False
        assert "out of range" in msg

    def test_set_numeric_value(self):
        doc = _make_doc()
        ok, _ = set_cell_value(doc, 0, 0, 0, 42, "float")
        assert ok is True
        assert doc.sheets[0].rows[0].cells[0].value == 42
        assert doc.sheets[0].rows[0].cells[0].value_type == "float"

    def test_set_roundtrip(self, tmp_path):
        doc = _make_doc()
        set_cell_value(doc, 0, 0, 0, "Modified", "string")
        out = tmp_path / "modified.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert reloaded.sheets[0].rows[0].cells[0].text == "Modified"


class TestAddSheet:
    def test_add_sheet_appends(self):
        doc = _make_doc()
        ok, msg = add_sheet(doc, "New")
        assert ok is True
        assert len(doc.sheets) == 2
        assert doc.sheets[1].name == "New"

    def test_add_sheet_at_position(self):
        doc = _make_doc()
        ok, _ = add_sheet(doc, "First", position=0)
        assert ok is True
        assert doc.sheets[0].name == "First"
        assert doc.sheets[1].name == "Data"

    def test_add_duplicate_name_fails(self):
        doc = _make_doc()
        ok, msg = add_sheet(doc, "Data")
        assert ok is False
        assert "already exists" in msg

    def test_add_sheet_roundtrip(self, tmp_path):
        doc = _make_doc()
        add_sheet(doc, "Extra")
        out = tmp_path / "multi.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        names = [s.name for s in reloaded.sheets]
        assert "Data" in names
        assert "Extra" in names


class TestRemoveSheet:
    def test_remove_existing(self):
        doc = OdsDocument(sheets=[
            OdsSheet(name="A", rows=[]),
            OdsSheet(name="B", rows=[]),
        ])
        ok, msg = remove_sheet(doc, "A")
        assert ok is True
        assert len(doc.sheets) == 1
        assert doc.sheets[0].name == "B"

    def test_remove_nonexistent(self):
        doc = _make_doc()
        ok, msg = remove_sheet(doc, "NoSuch")
        assert ok is False
        assert "not found" in msg

    def test_remove_roundtrip(self, tmp_path):
        doc = OdsDocument(sheets=[
            OdsSheet(name="Keep", rows=[OdsRow(cells=[OdsCell(text="X")])]),
            OdsSheet(name="Remove", rows=[]),
        ])
        remove_sheet(doc, "Remove")
        out = tmp_path / "removed.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert len(reloaded.sheets) == 1
        assert reloaded.sheets[0].name == "Keep"


class TestRenameSheet:
    def test_rename_existing(self):
        doc = _make_doc()
        ok, msg = rename_sheet(doc, "Data", "Renamed")
        assert ok is True
        assert doc.sheets[0].name == "Renamed"

    def test_rename_to_existing_name_fails(self):
        doc = OdsDocument(sheets=[
            OdsSheet(name="A", rows=[]),
            OdsSheet(name="B", rows=[]),
        ])
        ok, msg = rename_sheet(doc, "A", "B")
        assert ok is False
        assert "already exists" in msg

    def test_rename_nonexistent(self):
        doc = _make_doc()
        ok, msg = rename_sheet(doc, "NoSuch", "New")
        assert ok is False
        assert "not found" in msg

    def test_rename_roundtrip(self, tmp_path):
        doc = _make_doc()
        rename_sheet(doc, "Data", "MySheet")
        out = tmp_path / "renamed.ods"
        write_ods(doc, out)
        reloaded = parse_ods_strict(out)
        assert reloaded.sheets[0].name == "MySheet"
