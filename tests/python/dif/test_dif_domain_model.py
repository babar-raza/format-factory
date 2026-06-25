"""V53 compliance tests for DifModelDocument domain model class.

spec_qname must be accessible at class level (ClassVar) and not require instantiation.
"""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.dif.models import DifModelDocument, DifDoc


class TestDifModelDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert DifModelDocument.spec_qname == "dif:document"

    def test_spec_qname_is_classvar(self):
        ann = DifModelDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(DifModelDocument.spec_qname, str)

    def test_spec_qname_has_namespace(self):
        assert ":" in DifModelDocument.spec_qname

    def test_spec_fact_ref_class_level(self):
        assert DifModelDocument.spec_fact_ref == "FACT-DIF-001"

    def test_alias_is_same_class(self):
        assert DifDoc is DifModelDocument

    def test_from_file_returns_model(self):
        sample = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
        doc = DifModelDocument.from_file(sample)
        assert isinstance(doc, DifModelDocument)

    def test_from_file_spec_qname_on_instance(self):
        sample = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
        doc = DifModelDocument.from_file(sample)
        assert doc.spec_qname == "dif:document"

    def test_from_file_vectors(self):
        sample = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
        doc = DifModelDocument.from_file(sample)
        assert doc.vectors >= 1

    def test_to_dict_has_required_keys(self):
        sample = _REPO / "samples/by-format/dif/valid/minimal-2x2.dif"
        doc = DifModelDocument.from_file(sample)
        d = doc.to_dict()
        assert "title" in d and "vectors" in d and "row_count" in d
