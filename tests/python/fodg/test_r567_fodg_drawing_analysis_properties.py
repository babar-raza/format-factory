"""R567: FODG drawing analysis properties — is_multi_page, has_multiple_shapes, shapes_per_page.

Tests for FodgDocument drawing analysis properties added in R567.
Spec refs: SAL-FODG-00001.
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


class TestIsMultiPage:
    def test_two_pages_is_multi(self):
        doc = _make_doc(page_count=2)
        assert doc.is_multi_page is True

    def test_one_page_not_multi(self):
        doc = _make_doc(page_count=1)
        assert doc.is_multi_page is False

    def test_zero_pages_not_multi(self):
        doc = _make_doc(page_count=0)
        assert doc.is_multi_page is False

    def test_five_pages_is_multi(self):
        doc = _make_doc(page_count=5)
        assert doc.is_multi_page is True

    def test_is_multi_page_type(self):
        doc = _make_doc(page_count=2)
        assert isinstance(doc.is_multi_page, bool)


class TestHasMultipleShapes:
    def test_two_shapes_multiple(self):
        doc = _make_doc(page_count=1, shapes_total=2)
        assert doc.has_multiple_shapes is True

    def test_one_shape_not_multiple(self):
        doc = _make_doc(page_count=1, shapes_total=1)
        assert doc.has_multiple_shapes is False

    def test_zero_shapes_not_multiple(self):
        doc = _make_doc(page_count=1, shapes_total=0)
        assert doc.has_multiple_shapes is False

    def test_ten_shapes_multiple(self):
        doc = _make_doc(page_count=2, shapes_total=10)
        assert doc.has_multiple_shapes is True

    def test_has_multiple_shapes_type(self):
        doc = _make_doc(page_count=1, shapes_total=0)
        assert isinstance(doc.has_multiple_shapes, bool)


class TestShapesPerPage:
    def test_zero_pages_returns_zero(self):
        doc = _make_doc(page_count=0, shapes_total=0)
        assert doc.shapes_per_page == 0.0

    def test_one_page_two_shapes(self):
        doc = _make_doc(page_count=1, shapes_total=2)
        assert doc.shapes_per_page == 2.0

    def test_two_pages_four_shapes(self):
        doc = _make_doc(page_count=2, shapes_total=4)
        assert doc.shapes_per_page == 2.0

    def test_three_pages_nine_shapes(self):
        doc = _make_doc(page_count=3, shapes_total=9)
        assert doc.shapes_per_page == 3.0

    def test_fractional_ratio(self):
        doc = _make_doc(page_count=2, shapes_total=3)
        assert doc.shapes_per_page == 1.5

    def test_shapes_per_page_type(self):
        doc = _make_doc(page_count=1, shapes_total=1)
        assert isinstance(doc.shapes_per_page, float)

    def test_zero_shapes_one_page(self):
        doc = _make_doc(page_count=1, shapes_total=0)
        assert doc.shapes_per_page == 0.0


class TestDrawingAnalysisConsistency:
    def test_multi_page_implies_not_single_page(self):
        doc = _make_doc(page_count=3)
        assert doc.is_multi_page
        assert not doc.is_single_page
        assert not doc.is_empty

    def test_multiple_shapes_implies_has_shapes(self):
        doc = _make_doc(page_count=1, shapes_total=3)
        assert doc.has_multiple_shapes
        assert doc.has_shapes

    def test_shapes_per_page_nonnegative(self):
        for p in range(5):
            for s in range(5):
                doc = _make_doc(page_count=p, shapes_total=s)
                assert doc.shapes_per_page >= 0.0

    def test_from_file_minimal(self):
        doc = FodgDocument.from_file(SAMPLES / "minimal-drawing.fodg")
        assert isinstance(doc.is_multi_page, bool)
        assert isinstance(doc.has_multiple_shapes, bool)
        assert isinstance(doc.shapes_per_page, float)
