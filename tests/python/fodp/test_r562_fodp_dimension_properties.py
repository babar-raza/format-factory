"""R562: FODP dimension properties — is_empty, is_single_page, is_multi_page.

Tests for FodpDocument dimension properties added in R562.
Spec refs: ODF-FACT-BODY.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.models import FodpDocument

SAMPLES = Path("samples/by-format/fodp")


def _make_doc(page_count=0):
    """Build a minimal FodpDocument from a dict."""
    pages = [{"name": f"Slide{i}", "shape_count": 0, "text_content": []} for i in range(page_count)]
    return FodpDocument({"is_fodp": True, "page_count": page_count, "pages": pages, "styles_count": 0})


class TestIsEmpty:
    def test_no_slides_is_empty(self):
        doc = _make_doc(page_count=0)
        assert doc.is_empty is True

    def test_one_slide_not_empty(self):
        doc = _make_doc(page_count=1)
        assert doc.is_empty is False

    def test_multiple_slides_not_empty(self):
        doc = _make_doc(page_count=3)
        assert doc.is_empty is False

    def test_is_empty_type(self):
        doc = _make_doc(page_count=0)
        assert isinstance(doc.is_empty, bool)


class TestIsSinglePage:
    def test_one_slide_is_single(self):
        doc = _make_doc(page_count=1)
        assert doc.is_single_page is True

    def test_zero_slides_not_single(self):
        doc = _make_doc(page_count=0)
        assert doc.is_single_page is False

    def test_two_slides_not_single(self):
        doc = _make_doc(page_count=2)
        assert doc.is_single_page is False

    def test_is_single_page_type(self):
        doc = _make_doc(page_count=1)
        assert isinstance(doc.is_single_page, bool)


class TestIsMultiPage:
    def test_two_slides_is_multi(self):
        doc = _make_doc(page_count=2)
        assert doc.is_multi_page is True

    def test_one_slide_not_multi(self):
        doc = _make_doc(page_count=1)
        assert doc.is_multi_page is False

    def test_zero_slides_not_multi(self):
        doc = _make_doc(page_count=0)
        assert doc.is_multi_page is False

    def test_is_multi_page_type(self):
        doc = _make_doc(page_count=2)
        assert isinstance(doc.is_multi_page, bool)


class TestDimensionConsistency:
    def test_empty_not_single_not_multi(self):
        doc = _make_doc(page_count=0)
        assert doc.is_empty
        assert not doc.is_single_page
        assert not doc.is_multi_page

    def test_single_not_empty_not_multi(self):
        doc = _make_doc(page_count=1)
        assert not doc.is_empty
        assert doc.is_single_page
        assert not doc.is_multi_page

    def test_multi_not_empty_not_single(self):
        doc = _make_doc(page_count=3)
        assert not doc.is_empty
        assert not doc.is_single_page
        assert doc.is_multi_page

    def test_from_file_minimal(self):
        doc = FodpDocument.from_file(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(doc.is_empty, bool)
        assert isinstance(doc.is_single_page, bool)
        assert isinstance(doc.is_multi_page, bool)
