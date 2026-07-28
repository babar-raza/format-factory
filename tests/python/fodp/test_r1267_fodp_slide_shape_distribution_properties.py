"""Tests for R1267: FodpDocument slide shape distribution properties.

Properties under test:
    min_shapes_on_slide — minimum shapes on any slide (0 if no slides)
    slide_shape_range   — max_shapes_on_slide - min_shapes_on_slide
    has_uniform_slides  — all slides have same shape count

spec_fact_ref: SAL-FODP-00001
"""

import pytest
from fodp.models import FodpDocument


def _make_doc(shape_counts: list[int], titles: list[str] | None = None) -> FodpDocument:
    """Build FodpDocument stub with per-slide shape counts."""
    if titles is None:
        titles = [""] * len(shape_counts)
    pages = [
        {"shape_count": c, "title": t, "text_content": ""}
        for c, t in zip(shape_counts, titles)
    ]
    return FodpDocument({
        "is_fodp": True,
        "page_count": len(shape_counts),
        "styles_count": 0,
        "pages": pages,
    })


# ── min_shapes_on_slide ───────────────────────────────────────────────────────

class TestMinShapesOnSlide:
    def test_no_slides_returns_zero(self):
        doc = _make_doc([])
        assert doc.min_shapes_on_slide == 0

    def test_single_slide_min(self):
        doc = _make_doc([8])
        assert doc.min_shapes_on_slide == 8

    def test_picks_smallest(self):
        doc = _make_doc([3, 10, 7])
        assert doc.min_shapes_on_slide == 3

    def test_all_same(self):
        doc = _make_doc([5, 5, 5])
        assert doc.min_shapes_on_slide == 5

    def test_zero_on_one_slide(self):
        doc = _make_doc([0, 5, 10])
        assert doc.min_shapes_on_slide == 0


# ── slide_shape_range ─────────────────────────────────────────────────────────

class TestSlideShapeRange:
    def test_no_slides_range_zero(self):
        doc = _make_doc([])
        assert doc.slide_shape_range == 0

    def test_single_slide_range_zero(self):
        doc = _make_doc([4])
        assert doc.slide_shape_range == 0

    def test_equal_slides_range_zero(self):
        doc = _make_doc([6, 6, 6])
        assert doc.slide_shape_range == 0

    def test_varied_slides_range(self):
        doc = _make_doc([2, 12])
        assert doc.slide_shape_range == 10

    def test_range_is_max_minus_min(self):
        doc = _make_doc([1, 5, 15])
        assert doc.slide_shape_range == doc.max_shapes_on_slide - doc.min_shapes_on_slide


# ── has_uniform_slides ────────────────────────────────────────────────────────

class TestHasUniformSlides:
    def test_no_slides_is_uniform(self):
        doc = _make_doc([])
        assert doc.has_uniform_slides is True

    def test_single_slide_is_uniform(self):
        doc = _make_doc([3])
        assert doc.has_uniform_slides is True

    def test_equal_counts_uniform(self):
        doc = _make_doc([4, 4, 4])
        assert doc.has_uniform_slides is True

    def test_different_counts_not_uniform(self):
        doc = _make_doc([2, 8])
        assert doc.has_uniform_slides is False

    def test_one_empty_slide_not_uniform(self):
        doc = _make_doc([0, 5])
        assert doc.has_uniform_slides is False


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_uniform_implies_zero_range(self):
        doc = _make_doc([6, 6, 6])
        assert doc.has_uniform_slides is True
        assert doc.slide_shape_range == 0

    def test_nonzero_range_implies_not_uniform(self):
        doc = _make_doc([3, 9])
        assert doc.slide_shape_range > 0
        assert doc.has_uniform_slides is False

    def test_range_consistent_with_min_max(self):
        doc = _make_doc([2, 5, 11])
        assert doc.slide_shape_range == doc.max_shapes_on_slide - doc.min_shapes_on_slide
        assert doc.min_shapes_on_slide == 2
        assert doc.max_shapes_on_slide == 11
