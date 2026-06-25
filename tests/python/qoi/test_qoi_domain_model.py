"""V53 compliance tests for QoiDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.qoi.models import QoiDocument

_SAMPLE = _REPO / "samples/by-format/qoi/valid/1x1-red.qoi"


class TestQoiDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert QoiDocument.spec_qname == "qoi:image"

    def test_spec_qname_is_classvar(self):
        ann = QoiDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(QoiDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert QoiDocument.spec_fact_ref == "FACT-QOI-001"

    def test_from_file_returns_model(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert isinstance(doc, QoiDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "qoi:image"

    def test_from_file_dimensions(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert doc.width == 1 and doc.height == 1

    def test_to_dict_width_key(self):
        doc = QoiDocument.from_file(_SAMPLE)
        assert "width" in doc.to_dict()

