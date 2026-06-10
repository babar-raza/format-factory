"""
test_r162_ods_add_delete_row.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT24-001
Added: 2026-06-10

Tests for ODS writer APIs:
- add_row(doc, sheet_index, values, value_type) -> (bool, str)
- delete_row(doc, sheet_index, row) -> (bool, str)

Authority: ODS (OpenDocument Spreadsheet)
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell
from src.python.ods.ods_writer import add_row, delete_row


def _make_doc(rows_data=None):
    """Create a minimal OdsDocument with one sheet."""
    rows = []
    if rows_data:
        for row_vals in rows_data:
            cells = [OdsCell(value=v, value_type="string", text=str(v) if v else "")
                     for v in row_vals]
            rows.append(OdsRow(cells=cells))
    sheet = OdsSheet(name="Sheet1", rows=rows)
    return OdsDocument(sheets=[sheet])


# --- add_row tests ---

class TestAddRow:

    def test_add_row_basic(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 0, ["Alice", "Bob"])
        assert ok is True
        assert len(doc.sheets[0].rows) == 1
        assert doc.sheets[0].rows[0].cells[0].value == "Alice"
        assert doc.sheets[0].rows[0].cells[1].value == "Bob"

    def test_add_row_numeric_auto_types(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 0, [42, 3.14])
        assert ok is True
        assert doc.sheets[0].rows[0].cells[0].value_type == "float"
        assert doc.sheets[0].rows[0].cells[1].value_type == "float"

    def test_add_row_invalid_sheet_index(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 5, ["x"])
        assert ok is False
        assert "out of range" in msg.lower()

    def test_add_row_appends_to_existing(self):
        doc = _make_doc([["row1"]])
        ok, msg = add_row(doc, 0, ["row2"])
        assert ok is True
        assert len(doc.sheets[0].rows) == 2
        assert doc.sheets[0].rows[1].cells[0].value == "row2"

    def test_add_row_empty_values(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 0, [])
        assert ok is True
        assert len(doc.sheets[0].rows[0].cells) == 0


# --- delete_row tests ---

class TestDeleteRow:

    def test_delete_first_row(self):
        doc = _make_doc([["a"], ["b"], ["c"]])
        ok, msg = delete_row(doc, 0, 0)
        assert ok is True
        assert len(doc.sheets[0].rows) == 2
        assert doc.sheets[0].rows[0].cells[0].value == "b"

    def test_delete_last_row(self):
        doc = _make_doc([["a"], ["b"]])
        ok, msg = delete_row(doc, 0, 1)
        assert ok is True
        assert len(doc.sheets[0].rows) == 1
        assert doc.sheets[0].rows[0].cells[0].value == "a"

    def test_delete_invalid_sheet(self):
        doc = _make_doc([["a"]])
        ok, msg = delete_row(doc, 3, 0)
        assert ok is False

    def test_delete_invalid_row(self):
        doc = _make_doc([["a"]])
        ok, msg = delete_row(doc, 0, 5)
        assert ok is False
        assert "out of range" in msg.lower()

    def test_delete_only_row(self):
        doc = _make_doc([["only"]])
        ok, msg = delete_row(doc, 0, 0)
        assert ok is True
        assert len(doc.sheets[0].rows) == 0
