"""V53 compliance tests for SylkModelDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.sylk.models import SylkModelDocument

_SAMPLE = _REPO / "samples/by-format/sylk/valid/minimal-2x2.slk"


class TestSylkModelDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert SylkModelDocument.spec_qname == "sylk:document"

    def test_spec_qname_is_classvar(self):
        ann = SylkModelDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(SylkModelDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert SylkModelDocument.spec_fact_ref == "FACT-SYLK-001"

    def test_from_file_returns_model(self):
        doc = SylkModelDocument.from_file(_SAMPLE)
        assert isinstance(doc, SylkModelDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = SylkModelDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "sylk:document"

    def test_from_file_cell_count(self):
        doc = SylkModelDocument.from_file(_SAMPLE)
        assert doc.cell_count >= 1

    def test_to_dict_row_count_key(self):
        doc = SylkModelDocument.from_file(_SAMPLE)
        assert "row_count" in doc.to_dict()

