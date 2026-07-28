"""Tests for R1266: FodgDocument shape distribution analysis properties.

Properties under test:
    min_shapes_on_page  — minimum shapes on any page (0 if no pages)
    shape_range         — max_shapes_on_page - min_shapes_on_page
    is_uniform_density  — all pages have same shape count

spec_fact_ref: SAL-FODG-00001
"""

import pytest
from fodg.models import FodgDocument


def _make_doc(shape_counts_per_page: list[int]) -> FodgDocument:
    """Build a FodgDocument stub with given per-page shape counts."""
    pages = [{"shape_count": c} for c in shape_counts_per_page]
    total_shapes = sum(shape_counts_per_page)
    return FodgDocument({
        "format_id": "fodg",
        "is_fodg": True,
        "page_count": len(shape_counts_per_page),
        "pages": pages,
        "shapes_total": total_shapes,
    })


# ── min_shapes_on_page ────────────────────────────────────────────────────────

class TestMinShapesOnPage:
    def test_no_pages_returns_zero(self):
        doc = _make_doc([])
        assert doc.min_shapes_on_page == 0

    def test_single_page_min(self):
        doc = _make_doc([5])
        assert doc.min_shapes_on_page == 5

    def test_picks_smallest(self):
        doc = _make_doc([3, 10, 7])
        assert doc.min_shapes_on_page == 3

    def test_all_same_equals_max(self):
        doc = _make_doc([8, 8, 8])
        assert doc.min_shapes_on_page == 8

    def test_zero_on_one_page(self):
        doc = _make_doc([0, 5, 10])
        assert doc.min_shapes_on_page == 0


# ── shape_range ───────────────────────────────────────────────────────────────

class TestShapeRange:
    def test_no_pages_range_zero(self):
        doc = _make_doc([])
        assert doc.shape_range == 0

    def test_single_page_range_zero(self):
        doc = _make_doc([7])
        assert doc.shape_range == 0

    def test_equal_pages_range_zero(self):
        doc = _make_doc([5, 5, 5])
        assert doc.shape_range == 0

    def test_varied_pages_range(self):
        doc = _make_doc([2, 12])
        assert doc.shape_range == 10

    def test_range_is_max_minus_min(self):
        doc = _make_doc([1, 5, 15])
        assert doc.shape_range == doc.max_shapes_on_page - doc.min_shapes_on_page


# ── is_uniform_density ────────────────────────────────────────────────────────

class TestIsUniformDensity:
    def test_no_pages_is_uniform(self):
        doc = _make_doc([])
        assert doc.is_uniform_density is True

    def test_single_page_is_uniform(self):
        doc = _make_doc([6])
        assert doc.is_uniform_density is True

    def test_equal_pages_uniform(self):
        doc = _make_doc([4, 4, 4])
        assert doc.is_uniform_density is True

    def test_different_counts_not_uniform(self):
        doc = _make_doc([2, 8])
        assert doc.is_uniform_density is False

    def test_one_empty_page_not_uniform(self):
        doc = _make_doc([0, 5])
        assert doc.is_uniform_density is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_implies_zero_range(self):
        doc = _make_doc([6, 6, 6])
        assert doc.is_uniform_density is True
        assert doc.shape_range == 0

    def test_nonzero_range_implies_not_uniform(self):
        doc = _make_doc([3, 9])
        assert doc.shape_range > 0
        assert doc.is_uniform_density is False

    def test_dense_and_nonuniform(self):
        doc = _make_doc([5, 20])  # avg = 12.5, dense; range = 15
        assert doc.is_dense is True
        assert doc.is_uniform_density is False
