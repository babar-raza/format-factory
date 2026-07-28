"""V53 compliance tests for XcfDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.xcf.models import XcfDocument

_SAMPLE = _REPO / "samples/by-format/xcf/valid/1x1-red-rgb.xcf"


class TestXcfDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert XcfDocument.spec_qname == "xcf:image"

    def test_spec_qname_is_classvar(self):
        ann = XcfDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(XcfDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert XcfDocument.spec_fact_ref == "SAL-XCF-00001"

    def test_from_file_returns_model(self):
        doc = XcfDocument.from_file(_SAMPLE)
        assert isinstance(doc, XcfDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = XcfDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "xcf:image"

    def test_from_file_dimensions(self):
        doc = XcfDocument.from_file(_SAMPLE)
        assert doc.width == 1 and doc.height == 1

    def test_to_dict_width_key(self):
        doc = XcfDocument.from_file(_SAMPLE)
        assert "width" in doc.to_dict()

