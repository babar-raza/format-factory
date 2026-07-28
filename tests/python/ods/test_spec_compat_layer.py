"""Behavioral tests for ODS spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.ods.Compat import OdsDocument, OdsSheet, OdsCell
from src.python.ods.spec.office.document import Document as SpecDocument
from src.python.ods.spec.table.table import Table as SpecTable
from src.python.ods.spec.table.table_cell import TableCell as SpecTableCell


_SAMPLE_DOC = {
    "sheet_count": 2,
    "sheets": [
        {"name": "Sheet1", "rows": []},
        {"name": "Sheet2", "rows": []},
    ],
    "is_ods": True,
}
_SAMPLE_SHEET = {"name": "Sheet1", "rows": []}
_SAMPLE_CELL = {"value": "Hello", "value_type": "string", "col_span": 1}


class TestOdsDocumentMetadata:
    def test_spec_qname(self):
        assert OdsDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert "SAL-ODS" in OdsDocument.spec_fact_ref

    def test_namespace_uri_present(self):
        assert "oasis" in OdsDocument.namespace_uri


class TestOdsDocumentBehavior:
    def test_instantiation(self):
        doc = OdsDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_sheet_count(self):
        doc = OdsDocument(_SAMPLE_DOC)
        assert doc.sheet_count == 2

    def test_is_ods(self):
        doc = OdsDocument(_SAMPLE_DOC)
        assert doc.is_ods is True

    def test_to_dict(self):
        doc = OdsDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        doc = OdsDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = OdsDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestOdsSheetBehavior:
    def test_instantiation(self):
        s = OdsSheet(_SAMPLE_SHEET)
        assert s is not None

    def test_spec_qname(self):
        assert OdsSheet.spec_qname == "table:table"

    def test_name_property(self):
        s = OdsSheet(_SAMPLE_SHEET)
        assert s.name == "Sheet1"

    def test_inherits_spec_class(self):
        s = OdsSheet(_SAMPLE_SHEET)
        assert isinstance(s, SpecTable)

    def test_repr_nonempty(self):
        s = OdsSheet(_SAMPLE_SHEET)
        assert repr(s)


class TestOdsCellBehavior:
    def test_instantiation(self):
        c = OdsCell(_SAMPLE_CELL)
        assert c is not None

    def test_spec_qname(self):
        assert OdsCell.spec_qname == "table:table-cell"

    def test_value_property(self):
        c = OdsCell(_SAMPLE_CELL)
        assert c.value == "Hello"

    def test_inherits_spec_class(self):
        c = OdsCell(_SAMPLE_CELL)
        assert isinstance(c, SpecTableCell)

    def test_repr_nonempty(self):
        c = OdsCell(_SAMPLE_CELL)
        assert repr(c)
