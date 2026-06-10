"""Tests for ODS set_cell_value (edit-save-roundtrip).

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT18-001
Covers: set_cell_value on OdsDocument, write, re-parse verification
"""

import sys
import tempfile
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsDocument, OdsSheet, OdsRow, OdsCell, parse_ods_strict
from ods.ods_writer import write_ods, set_cell_value


def _make_doc():
    return OdsDocument(
        sheets=[OdsSheet(name="Sheet1", rows=[
            OdsRow(cells=[
                OdsCell(value="A", value_type="string", text="A"),
                OdsCell(value="B", value_type="string", text="B"),
            ]),
            OdsRow(cells=[
                OdsCell(value=1.0, value_type="float", text="1"),
                OdsCell(value=2.0, value_type="float", text="2"),
            ]),
        ])],
        path="",
    )


class TestSetCellValue:
    def test_set_string_cell(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 0, 0, 0, "Hello", "string")
        assert ok
        assert doc.sheets[0].rows[0].cells[0].value == "Hello"

    def test_set_float_cell(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 0, 1, 0, 99.5, "float")
        assert ok
        assert doc.sheets[0].rows[1].cells[0].value == 99.5

    def test_set_out_of_range_sheet_returns_false(self):
        doc = _make_doc()
        ok, msg = set_cell_value(doc, 5, 0, 0, "x")
        assert not ok

    def test_set_extends_rows(self):
        doc = _make_doc()
        ok, _ = set_cell_value(doc, 0, 10, 0, "extended")
        assert ok
        assert len(doc.sheets[0].rows) == 11

    def test_set_extends_cols(self):
        doc = _make_doc()
        ok, _ = set_cell_value(doc, 0, 0, 10, "wide")
        assert ok
        assert len(doc.sheets[0].rows[0].cells) == 11


class TestSetCellRoundtrip:
    def test_edit_write_parse_roundtrip(self):
        doc = _make_doc()
        set_cell_value(doc, 0, 0, 0, "EDITED", "string")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[0].value == "EDITED"
        finally:
            out.unlink(missing_ok=True)

    def test_edit_float_write_parse_roundtrip(self):
        doc = _make_doc()
        set_cell_value(doc, 0, 1, 1, 42.0, "float")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[1].cells[1].value == 42.0
        finally:
            out.unlink(missing_ok=True)

    def test_edit_preserves_other_cells(self):
        doc = _make_doc()
        set_cell_value(doc, 0, 0, 0, "NEW", "string")
        with tempfile.NamedTemporaryFile(suffix=".ods", delete=False) as f:
            out = Path(f.name)
        try:
            write_ods(doc, out)
            doc2 = parse_ods_strict(out)
            assert doc2.sheets[0].rows[0].cells[1].value == "B"
            assert doc2.sheets[0].rows[1].cells[0].value == 1.0
        finally:
            out.unlink(missing_ok=True)
