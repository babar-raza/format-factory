"""V53 compliance tests for OdsModelDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ods.models import OdsModelDocument

_SAMPLE = _REPO / "samples/by-format/ods/valid/minimal-spreadsheet.ods"


class TestOdsModelDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert OdsModelDocument.spec_qname == "office:document"

    def test_spec_qname_is_classvar(self):
        ann = OdsModelDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(OdsModelDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert OdsModelDocument.spec_fact_ref == "FACT-ODS-001"

    def test_from_file_returns_model(self):
        doc = OdsModelDocument.from_file(_SAMPLE)
        assert isinstance(doc, OdsModelDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = OdsModelDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "office:document"

    def test_from_file_sheet_count(self):
        doc = OdsModelDocument.from_file(_SAMPLE)
        assert doc.sheet_count >= 1

    def test_to_dict_sheet_count_key(self):
        doc = OdsModelDocument.from_file(_SAMPLE)
        assert "sheet_count" in doc.to_dict()

