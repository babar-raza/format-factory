"""V53 compliance tests for OdtModelDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.odt.models import OdtModelDocument

_SAMPLE = _REPO / "samples/by-format/odt/valid/two-paragraphs.odt"


class TestOdtModelDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert OdtModelDocument.spec_qname == "office:document"

    def test_spec_qname_is_classvar(self):
        ann = OdtModelDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(OdtModelDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert OdtModelDocument.spec_fact_ref == "FACT-ODT-001"

    def test_from_file_returns_model(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert isinstance(doc, OdtModelDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "office:document"

    def test_from_file_paragraph_count(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert doc.paragraph_count >= 1

    def test_to_dict_paragraph_count_key(self):
        doc = OdtModelDocument.from_file(_SAMPLE)
        assert "paragraph_count" in doc.to_dict()

