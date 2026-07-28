"""Behavioral tests for FODS spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fods.Compat import FodsDocument, FodsSheet, FodsCell
from src.python.fods.spec.office.document import Document as SpecDocument
from src.python.fods.spec.table.table import Table as SpecTable
from src.python.fods.spec.table.table_cell import TableCell as SpecTableCell


class TestFodsDocumentMetadata:
    def test_spec_qname(self):
        assert FodsDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert FodsDocument.spec_fact_ref == "SAL-FODS-00001"

    def test_namespace_uri_present(self):
        assert "oasis" in FodsDocument.namespace_uri


class TestFodsDocumentBehavior:
    def test_instantiation_no_args(self):
        doc = FodsDocument()
        assert doc is not None

    def test_inherits_spec_class(self):
        doc = FodsDocument()
        assert isinstance(doc, SpecDocument)

    def test_repr_nonempty(self):
        doc = FodsDocument()
        assert repr(doc)


class TestFodsSheetMetadata:
    def test_spec_qname(self):
        assert FodsSheet.spec_qname == "table:table"

    def test_spec_fact_ref(self):
        assert FodsSheet.spec_fact_ref == "SAL-FODS-00004"

    def test_namespace_uri_present(self):
        assert FodsSheet.namespace_uri


class TestFodsSheetBehavior:
    def test_instantiation_no_args(self):
        sheet = FodsSheet()
        assert sheet is not None

    def test_inherits_spec_class(self):
        sheet = FodsSheet()
        assert isinstance(sheet, SpecTable)

    def test_repr_nonempty(self):
        sheet = FodsSheet()
        assert repr(sheet)


class TestFodsCellMetadata:
    def test_spec_qname(self):
        assert FodsCell.spec_qname == "table:table-cell"

    def test_spec_fact_ref(self):
        assert FodsCell.spec_fact_ref == "SAL-FODS-00006"

    def test_namespace_uri_present(self):
        assert FodsCell.namespace_uri


class TestFodsCellBehavior:
    def test_instantiation_no_args(self):
        cell = FodsCell()
        assert cell is not None

    def test_inherits_spec_class(self):
        cell = FodsCell()
        assert isinstance(cell, SpecTableCell)

    def test_repr_nonempty(self):
        cell = FodsCell()
        assert repr(cell)
