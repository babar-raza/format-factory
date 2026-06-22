"""Behavioral tests for FODG spec/Compat layer (TC-PH-004)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent))

from src.python.fodg.Compat import FodgDocument, FodgPage
from src.python.fodg.spec.office.document import Document as SpecDocument
from src.python.fodg.spec.draw.page import Page as SpecPage


_SAMPLE_DOC = {
    "mime_type": "application/vnd.oasis.opendocument.graphics",
    "is_fodg": True,
    "page_count": 2,
    "shapes_total": 5,
    "pages": [{"name": "Page1", "shape_count": 3, "shapes": []}, {"name": "Page2", "shape_count": 2, "shapes": []}],
}
_SAMPLE_PAGE = {"name": "Page1", "shape_count": 3, "shapes": []}


class TestFodgDocumentMetadata:
    def test_spec_qname(self):
        assert FodgDocument.spec_qname == "office:document"

    def test_spec_fact_ref(self):
        assert "FACT-FODG" in FodgDocument.spec_fact_ref

    def test_namespace_uri_present(self):
        assert "oasis" in FodgDocument.namespace_uri


class TestFodgDocumentBehavior:
    def test_instantiation(self):
        doc = FodgDocument(_SAMPLE_DOC)
        assert doc is not None

    def test_is_fodg_property(self):
        doc = FodgDocument(_SAMPLE_DOC)
        assert doc.is_fodg is True

    def test_page_count(self):
        doc = FodgDocument(_SAMPLE_DOC)
        assert doc.page_count == 2

    def test_to_dict(self):
        doc = FodgDocument(_SAMPLE_DOC)
        d = doc.to_dict()
        assert isinstance(d, dict)

    def test_repr_nonempty(self):
        doc = FodgDocument(_SAMPLE_DOC)
        assert repr(doc)

    def test_inherits_spec_class(self):
        doc = FodgDocument(_SAMPLE_DOC)
        assert isinstance(doc, SpecDocument)


class TestFodgPageBehavior:
    def test_instantiation(self):
        p = FodgPage(_SAMPLE_PAGE)
        assert p is not None

    def test_spec_qname(self):
        assert FodgPage.spec_qname == "draw:page"

    def test_name_property(self):
        p = FodgPage(_SAMPLE_PAGE)
        assert p.name == "Page1"

    def test_shape_count(self):
        p = FodgPage(_SAMPLE_PAGE)
        assert p.shape_count == 3

    def test_inherits_spec_class(self):
        p = FodgPage(_SAMPLE_PAGE)
        assert isinstance(p, SpecPage)

    def test_repr_nonempty(self):
        p = FodgPage(_SAMPLE_PAGE)
        assert repr(p)
