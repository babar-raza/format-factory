"""Tests for spec_qname class-level attributes on SYLK model classes.

Gap closure: GAP-PROD-INV-QNAME-001 (class-level spec_qname missing in SYLK)
V53 compliance: spec_qname must be accessible as ClassName.spec_qname (no instantiation).
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import SylkCell, SylkDocument


class TestSylkClassLevelSpecQname:
    def test_sylk_cell_spec_qname_class_access(self):
        assert SylkCell.spec_qname == "slk:cell"

    def test_sylk_document_spec_qname_class_access(self):
        assert SylkDocument.spec_qname == "sylk:document"

    def test_sylk_cell_spec_qname_is_string(self):
        assert isinstance(SylkCell.spec_qname, str)

    def test_sylk_document_spec_qname_is_string(self):
        assert isinstance(SylkDocument.spec_qname, str)

    def test_sylk_cell_spec_qname_matches_instance(self):
        instance = SylkCell()
        assert instance.spec_qname == SylkCell.spec_qname

    def test_sylk_document_spec_qname_matches_instance(self):
        instance = SylkDocument()
        assert instance.spec_qname == SylkDocument.spec_qname

    def test_sylk_cell_qname_namespace(self):
        assert ":" in SylkCell.spec_qname

    def test_sylk_document_qname_namespace(self):
        assert ":" in SylkDocument.spec_qname
