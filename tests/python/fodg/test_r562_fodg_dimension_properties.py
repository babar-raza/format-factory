"""R562: FODG dimension properties — is_empty, is_single_page, has_shapes.

Tests for FodgDocument dimension properties added in R562.
Spec refs: ODF-FACT-BODY.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.models import FodgDocument

SAMPLES = Path("samples/by-format/fodg")


def _make_doc(page_count=0, shapes_total=0):
    """Build a minimal FodgDocument from a dict."""
    pages = [{"name": f"Page{i}", "shape_count": 0, "text_content": []} for i in range(page_count)]
    return FodgDocument({"is_fodg": True, "page_count": page_count, "pages": pages, "shapes_total": shapes_total})


class TestIsEmpty:
    def test_no_pages_is_empty(self):
        doc = _make_doc(page_count=0)
        assert doc.is_empty is True

    def test_one_page_not_empty(self):
        doc = _make_doc(page_count=1)
        assert doc.is_empty is False

    def test_multiple_pages_not_empty(self):
        doc = _make_doc(page_count=3)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(page_count=0)
        assert isinstance(doc.is_empty, bool)


class TestIsSinglePage:
    def test_one_page_is_single(self):
        doc = _make_doc(page_count=1)
        assert doc.is_single_page is True

    def test_zero_pages_not_single(self):
        doc = _make_doc(page_count=0)
        assert doc.is_single_page is False

    def test_two_pages_not_single(self):
        doc = _make_doc(page_count=2)
        assert doc.is_single_page is False

    def test_is_single_page_type(self):
        doc = _make_doc(page_count=1)
        assert isinstance(doc.is_single_page, bool)


class TestHasShapes:
    def test_shapes_present(self):
        doc = _make_doc(page_count=1, shapes_total=3)
        assert doc.has_shapes is True

    def test_no_shapes(self):
        doc = _make_doc(page_count=1, shapes_total=0)
        assert doc.has_shapes is False

    def test_empty_doc_no_shapes(self):
        doc = _make_doc(page_count=0, shapes_total=0)
        assert doc.has_shapes is False

    def test_has_shapes_type(self):
        doc = _make_doc(page_count=1, shapes_total=1)
        assert isinstance(doc.has_shapes, bool)


class TestDimensionConsistency:
    def test_empty_not_single(self):
        doc = _make_doc(page_count=0)
        assert doc.is_empty
        assert not doc.is_single_page

    def test_single_not_empty(self):
        doc = _make_doc(page_count=1)
        assert not doc.is_empty
        assert doc.is_single_page

    def test_from_file_minimal(self):
        doc = FodgDocument.from_file(SAMPLES / "minimal-drawing.fodg")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_page, bool)
        assert isinstance(doc.has_shapes, bool)
