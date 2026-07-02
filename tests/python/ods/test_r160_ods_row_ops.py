"""Tests for ODS add_row and delete_row.

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT20-001
Covers: row manipulation operations with roundtrip verification
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, parse_ods_strict
from ods.ods_writer import write_ods, add_row, delete_row


def _make_doc():
    return OdsDocument(
        sheets=[
            OdsSheet(name="Sheet1", rows=[
                OdsRow(cells=[
                    OdsCell(value="Name", value_type="string", text="Name"),
                    OdsCell(value="Age", value_type="string", text="Age"),
                ]),
                OdsRow(cells=[
                    OdsCell(value="Alice", value_type="string", text="Alice"),
                    OdsCell(value=30, value_type="float", text="30"),
                ]),
            ]),
        ],
        path="",
    )


class TestAddRow:
    def test_add_row_increases_count(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 0, ["Bob", 25])
        assert ok is not None
        assert len(doc.sheets[0].rows) == 3

    def test_add_row_values(self):
        doc = _make_doc()
        add_row(doc, 0, ["Charlie", 35])
        row = doc.sheets[0].rows[2]
        assert row.cells[0].value == "Charlie"
        assert row.cells[1].value == 35

    def test_add_row_bad_sheet(self):
        doc = _make_doc()
        ok, msg = add_row(doc, 5, ["X"])
        assert not bool(ok)

    def test_add_row_roundtrip(self):
        doc = _make_doc()
        add_row(doc, 0, ["Dave", 40])
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets[0].rows) == 3
            cells = doc2.sheets[0].rows[2].cells
            assert cells[0].text == "Dave"
        finally:
            out.unlink(missing_ok=True)


class TestDeleteRow:
    def test_delete_row_decreases_count(self):
        doc = _make_doc()
        ok, msg = delete_row(doc, 0, 1)
        assert ok is not None
        assert len(doc.sheets[0].rows) == 1

    def test_delete_row_preserves_other(self):
        doc = _make_doc()
        delete_row(doc, 0, 1)
        assert doc.sheets[0].rows[0].cells[0].value == "Name"

    def test_delete_row_bad_sheet(self):
        doc = _make_doc()
        ok, msg = delete_row(doc, 5, 0)
        assert not bool(ok)

    def test_delete_row_bad_index(self):
        doc = _make_doc()
        ok, msg = delete_row(doc, 0, 10)
        assert not bool(ok)

    def test_delete_row_roundtrip(self):
        doc = _make_doc()
        delete_row(doc, 0, 1)
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert len(doc2.sheets[0].rows) == 1
            assert doc2.sheets[0].rows[0].cells[0].text == "Name"
        finally:
            out.unlink(missing_ok=True)
