"""Tests for spec_qname class-level attributes on ODT model classes.

Gap closure: GAP-PROD-INV-QNAME-001 (class-level spec_qname missing in ODT)
V53 compliance: spec_qname must be accessible as ClassName.spec_qname (no instantiation).
"""
from __future__ import annotations

from pathlib import Path
import sys

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO / "src" / "python") not in sys.path:
    sys.path.insert(0, str(_REPO / "src" / "python"))

from odt.odt_parser import OdtParagraph, OdtHeading, OdtListItem, OdtDocument


class TestOdtClassLevelSpecQname:
    def test_odt_paragraph_spec_qname_class_access(self):
        assert OdtParagraph.spec_qname == "text:p"

    def test_odt_heading_spec_qname_class_access(self):
        assert OdtHeading.spec_qname == "text:h"

    def test_odt_list_item_spec_qname_class_access(self):
        assert OdtListItem.spec_qname == "text:list-item"

    def test_odt_document_spec_qname_class_access(self):
        assert OdtDocument.spec_qname == "office:document"

    def test_odt_paragraph_spec_qname_is_string(self):
        assert isinstance(OdtParagraph.spec_qname, str)

    def test_odt_heading_spec_qname_is_string(self):
        assert isinstance(OdtHeading.spec_qname, str)

    def test_odt_document_spec_qname_is_string(self):
        assert isinstance(OdtDocument.spec_qname, str)

    def test_odt_paragraph_spec_qname_matches_instance(self):
        instance = OdtParagraph(text="hello")
        assert instance.spec_qname == OdtParagraph.spec_qname

    def test_odt_heading_spec_qname_matches_instance(self):
        instance = OdtHeading(text="title", level=1)
        assert instance.spec_qname == OdtHeading.spec_qname

    def test_odt_document_spec_qname_matches_instance(self):
        instance = OdtDocument()
        assert instance.spec_qname == OdtDocument.spec_qname

    def test_odt_qnames_follow_odf_namespace(self):
        assert OdtParagraph.spec_qname.startswith("text:")
        assert OdtHeading.spec_qname.startswith("text:")
        assert OdtListItem.spec_qname.startswith("text:")
        assert OdtDocument.spec_qname.startswith("office:")
