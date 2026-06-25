"""Tests for spec_qname class-level attributes on ODS model classes.

Gap closure: GAP-PROD-INV-QNAME-001 (class-level spec_qname missing in ODS)
V53 compliance: spec_qname must be accessible as ClassName.spec_qname (no instantiation).
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from ods.ods_parser import OdsCell, OdsRow, OdsSheet, OdsDocument


class TestOdsClassLevelSpecQname:
    def test_ods_cell_spec_qname_class_access(self):
        assert OdsCell.spec_qname == "table:table-cell"

    def test_ods_row_spec_qname_class_access(self):
        assert OdsRow.spec_qname == "table:table-row"

    def test_ods_sheet_spec_qname_class_access(self):
        assert OdsSheet.spec_qname == "table:table"

    def test_ods_document_spec_qname_class_access(self):
        assert OdsDocument.spec_qname == "office:document"

    def test_ods_cell_spec_qname_is_string(self):
        assert isinstance(OdsCell.spec_qname, str)

    def test_ods_row_spec_qname_is_string(self):
        assert isinstance(OdsRow.spec_qname, str)

    def test_ods_sheet_spec_qname_is_string(self):
        assert isinstance(OdsSheet.spec_qname, str)

    def test_ods_document_spec_qname_is_string(self):
        assert isinstance(OdsDocument.spec_qname, str)

    def test_ods_cell_spec_qname_matches_instance(self):
        instance = OdsCell()
        assert instance.spec_qname == OdsCell.spec_qname

    def test_ods_sheet_spec_qname_matches_instance(self):
        instance = OdsSheet()
        assert instance.spec_qname == OdsSheet.spec_qname

    def test_ods_document_spec_qname_matches_instance(self):
        instance = OdsDocument()
        assert instance.spec_qname == OdsDocument.spec_qname

    def test_ods_qnames_follow_odf_namespace(self):
        assert OdsCell.spec_qname.startswith("table:")
        assert OdsRow.spec_qname.startswith("table:")
        assert OdsSheet.spec_qname.startswith("table:")
        assert OdsDocument.spec_qname.startswith("office:")
