"""V53 compliance tests for PbmDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.pbm.models import PbmDocument

_SAMPLE = _REPO / "samples/by-format/pbm/valid/2x2-checker.pbm"


class TestPbmDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert PbmDocument.spec_qname == "pbm:image"

    def test_spec_qname_is_classvar(self):
        ann = PbmDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(PbmDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert PbmDocument.spec_fact_ref == "FACT-PBM-001"

    def test_from_file_returns_model(self):
        doc = PbmDocument.from_file(_SAMPLE)
        assert isinstance(doc, PbmDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = PbmDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "pbm:image"

    def test_from_file_dimensions(self):
        doc = PbmDocument.from_file(_SAMPLE)
        assert doc.width == 2 and doc.height == 2

    def test_to_dict_width_key(self):
        doc = PbmDocument.from_file(_SAMPLE)
        assert "width" in doc.to_dict()

