"""Behavioral tests for FODP spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fodp.Compat import FodpDocument, FodpPage
from src.python.fodp.spec.office.document import Document as SpecDocument
from src.python.fodp.spec.draw.page import Page as SpecPage


_SAMPLE_DOC = {
    "mime_type": "application/vnd.oasis.opendocument.presentation",
    "page_count": 3,
    "styles_count": 10,
    "pages": [{"name": "Slide1", "layout": "Title", "shape_count": 2, "shapes": []}],
}
_SAMPLE_PAGE = {"name": "Slide1", "layout": "Title", "shape_count": 2, "shapes": []}


class TestFodpDocumentMetadata:
    def test_spec_qname(self):
        assert FodpDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert "FACT-FODP" in FodpDocument.spec_fact_ref

    def test_namespace_uri_present(self):
        assert "oasis" in FodpDocument.namespace_uri


class TestFodpDocumentBehavior:
    def test_instantiation(self):
        doc = FodpDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_is_fodp_property(self):
        doc = FodpDocument(_SAMPLE_DOC)
        assert doc.is_fodp is True

    def test_page_count(self):
        doc = FodpDocument(_SAMPLE_DOC)
        assert doc.page_count == 3

    def test_to_dict(self):
        doc = FodpDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        doc = FodpDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = FodpDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestFodpPageBehavior:
    def test_instantiation(self):
        p = FodpPage(_SAMPLE_PAGE)
        assert p is not None

    def test_spec_qname(self):
        assert FodpPage.spec_qname == "draw:page"

    def test_name_property(self):
        p = FodpPage(_SAMPLE_PAGE)
        assert p.name == "Slide1"

    def test_shape_count(self):
        p = FodpPage(_SAMPLE_PAGE)
        assert p.shape_count == 2

    def test_inherits_spec_class(self):
        p = FodpPage(_SAMPLE_PAGE)
        assert isinstance(p, SpecPage)

    def test_repr_nonempty(self):
        p = FodpPage(_SAMPLE_PAGE)
        assert repr(p)
