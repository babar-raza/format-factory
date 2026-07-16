"""V53 compliance tests for PgmDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.pgm.models import PgmDocument

_SAMPLE = _REPO / "samples/by-format/pgm/valid/2x2-gradient.pgm"


class TestPgmDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert PgmDocument.spec_qname == "pgm:image"

    def test_spec_qname_is_classvar(self):
        ann = PgmDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(PgmDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert PgmDocument.spec_fact_ref == "SAL-PGM-00001"

    def test_from_file_returns_model(self):
        doc = PgmDocument.from_file(_SAMPLE)
        assert isinstance(doc, PgmDocument)

    def test_from_file_spec_qname_on_instance(self):
        doc = PgmDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "pgm:image"

    def test_from_file_dimensions(self):
        doc = PgmDocument.from_file(_SAMPLE)
        assert doc.width == 2 and doc.height == 2

    def test_to_dict_width_key(self):
        doc = PgmDocument.from_file(_SAMPLE)
        assert "width" in doc.to_dict()

