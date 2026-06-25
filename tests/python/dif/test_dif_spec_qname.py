"""Tests for spec_qname class-level attributes on DIF model classes.

Gap closure: GAP-PROD-INV-QNAME-001 (class-level spec_qname missing in DIF)
V53 compliance: spec_qname must be accessible as ClassName.spec_qname (no instantiation).
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from dif.dif_parser import DifCell, DifDocument


class TestDifClassLevelSpecQname:
    def test_dif_cell_spec_qname_class_access(self):
        assert DifCell.spec_qname == "dif:cell"

    def test_dif_document_spec_qname_class_access(self):
        assert DifDocument.spec_qname == "dif:document"

    def test_dif_cell_spec_qname_is_string(self):
        assert isinstance(DifCell.spec_qname, str)

    def test_dif_document_spec_qname_is_string(self):
        assert isinstance(DifDocument.spec_qname, str)

    def test_dif_cell_spec_qname_matches_instance(self):
        instance = DifCell()
        assert instance.spec_qname == DifCell.spec_qname

    def test_dif_document_spec_qname_matches_instance(self):
        instance = DifDocument()
        assert instance.spec_qname == DifDocument.spec_qname

    def test_dif_cell_qname_namespace(self):
        assert DifCell.spec_qname.startswith("dif:")

    def test_dif_document_qname_namespace(self):
        assert DifDocument.spec_qname.startswith("dif:")
