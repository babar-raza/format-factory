"""V53 compliance tests for PpmDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.ppm.models import PpmDocument

_SAMPLE = _REPO / "samples/by-format/ppm/valid/2x2-rgbw.ppm"


class TestPpmDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert PpmDocument.spec_qname == "ppm:image"

    def test_spec_qname_is_classvar(self):
        ann = PpmDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(PpmDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert PpmDocument.spec_fact_ref == "FACT-PPM-001"

    def test_from_file_returns_model(self):
        doc = PpmDocument.from_file(_SAMPLE)
        assert isinstance(doc, PpmDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = PpmDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "ppm:image"

    def test_from_file_dimensions(self):
        doc = PpmDocument.from_file(_SAMPLE)
        assert doc.width == 2 and doc.height == 2

    def test_to_dict_width_key(self):
        doc = PpmDocument.from_file(_SAMPLE)
        assert "width" in doc.to_dict()

