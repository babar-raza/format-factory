"""V53 compliance tests for FodpDocument domain model class."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
from src.python.fodp.models import FodpDocument

_SAMPLE = _REPO / ".local/replay-r42/repo/samples/by-format/fodp/minimal-presentation.fodp"


class TestFodpDocumentSpecQname:
    def test_spec_qname_class_level_access(self):
        assert FodpDocument.spec_qname == "office:document"

    def test_spec_qname_is_classvar(self):
        ann = FodpDocument.__annotations__.get("spec_qname", "")
        assert "ClassVar" in str(ann)

    def test_spec_qname_is_string(self):
        assert isinstance(FodpDocument.spec_qname, str)

    def test_spec_fact_ref_class_level(self):
        assert FodpDocument.spec_fact_ref == "FACT-FODP-001"

    def test_from_file_returns_model(self):
        if not _SAMPLE.is_file():
            import pytest; pytest.skip(f"Sample file not present: {_SAMPLE}")
        doc = FodpDocument.from_file(_SAMPLE)
        assert isinstance(doc, FodpDocument)

    def test_from_file_spec_qname_on_instance(self):
        if not _SAMPLE.is_file():
            import pytest; pytest.skip(f"Sample file not present: {_SAMPLE}")
        doc = FodpDocument.from_file(_SAMPLE)
        assert doc.spec_qname == "office:document"

    def test_from_file_page_count(self):
        if not _SAMPLE.is_file():
            import pytest; pytest.skip(f"Sample file not present: {_SAMPLE}")
        doc = FodpDocument.from_file(_SAMPLE)
        assert doc.page_count >= 1

    def test_to_dict_page_count_key(self):
        if not _SAMPLE.is_file():
            import pytest; pytest.skip(f"Sample file not present: {_SAMPLE}")
        doc = FodpDocument.from_file(_SAMPLE)
        assert "page_count" in doc.to_dict()

