"""Tests for R1246: FodgDocument drawing density and complexity properties.

Properties under test:
    is_dense          — shapes_per_page > 10
    is_complex        — has_shapes AND is_multi_page
    max_shapes_on_page — max shape_count across pages (0 if no pages)

spec_fact_ref: FACT-FODG-001
"""

import pytest
from fodg.models import FodgDocument


def _make_page(name: str, shape_count: int) -> dict:
    return {"name": name, "style": "", "shape_count": shape_count, "text_content": ""}


def _make_doc(pages: list[dict] | None = None, shapes_total: int | None = None) -> FodgDocument:
    """Build a FodgDocument stub."""
    pages = pages or []
    if shapes_total is None:
        shapes_total = sum(p.get("shape_count", 0) for p in pages)
    return FodgDocument({
        "is_fodg": True,
        "page_count": len(pages),
        "pages": pages,
        "shapes_total": shapes_total,
    })


# ── is_dense ──────────────────────────────────────────────────────────────────

class TestIsDense:
    def test_11_shapes_per_page_is_dense(self):
        doc = _make_doc([_make_page("P1", 11)])
        assert doc.is_dense is True

    def test_exactly_10_shapes_not_dense(self):
        doc = _make_doc([_make_page("P1", 10)])  # shapes_per_page = 10.0, not > 10
        assert doc.is_dense is False

    def test_fewer_than_10_not_dense(self):
        doc = _make_doc([_make_page("P1", 5)])
        assert doc.is_dense is False

    def test_empty_not_dense(self):
        doc = _make_doc([])
        assert doc.is_dense is False

    def test_multi_page_dense(self):
        # total=25, pages=2 → avg=12.5 > 10
        doc = _make_doc([_make_page("P1", 13), _make_page("P2", 12)])
        assert doc.is_dense is True

    def test_multi_page_not_dense(self):
        # total=10, pages=2 → avg=5 <= 10
        doc = _make_doc([_make_page("P1", 5), _make_page("P2", 5)])
        assert doc.is_dense is False

    def test_zero_shapes_not_dense(self):
        doc = _make_doc([_make_page("P1", 0)])
        assert doc.is_dense is False


# ── is_complex ────────────────────────────────────────────────────────────────

class TestIsComplex:
    def test_shapes_and_multi_page_is_complex(self):
        doc = _make_doc([_make_page("P1", 3), _make_page("P2", 2)])
        assert doc.is_complex is True

    def test_shapes_single_page_not_complex(self):
        doc = _make_doc([_make_page("P1", 5)])
        assert doc.is_complex is False

    def test_no_shapes_multi_page_not_complex(self):
        doc = _make_doc([_make_page("P1", 0), _make_page("P2", 0)])
        assert doc.is_complex is False

    def test_empty_not_complex(self):
        doc = _make_doc([])
        assert doc.is_complex is False

    def test_three_pages_with_shapes_is_complex(self):
        doc = _make_doc([_make_page(f"P{i}", 2) for i in range(3)])
        assert doc.is_complex is True


# ── max_shapes_on_page ────────────────────────────────────────────────────────

class TestMaxShapesOnPage:
    def test_no_pages_returns_zero(self):
        doc = _make_doc([])
        assert doc.max_shapes_on_page == 0

    def test_single_page_returns_shape_count(self):
        doc = _make_doc([_make_page("P1", 7)])
        assert doc.max_shapes_on_page == 7

    def test_max_of_multiple_pages(self):
        doc = _make_doc([_make_page("P1", 3), _make_page("P2", 9), _make_page("P3", 5)])
        assert doc.max_shapes_on_page == 9

    def test_all_zero_pages(self):
        doc = _make_doc([_make_page("P1", 0), _make_page("P2", 0)])
        assert doc.max_shapes_on_page == 0

    def test_single_large_page(self):
        doc = _make_doc([_make_page("P1", 100)])
        assert doc.max_shapes_on_page == 100


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_dense_and_complex(self):
        doc = _make_doc([_make_page("P1", 15), _make_page("P2", 12)])
        assert doc.is_dense is True
        assert doc.is_complex is True

    def test_complex_not_dense(self):
        doc = _make_doc([_make_page("P1", 3), _make_page("P2", 2)])
        assert doc.is_complex is True
        assert doc.is_dense is False

    def test_max_shapes_gte_avg(self):
        doc = _make_doc([_make_page("P1", 5), _make_page("P2", 15)])
        assert doc.max_shapes_on_page >= doc.shapes_per_page

    def test_dense_consistent_with_shapes_per_page(self):
        doc = _make_doc([_make_page("P1", 20)])
        assert doc.is_dense is True
        assert doc.shapes_per_page > 10
