"""Tests for R1247: FodpDocument scale and content classification properties.

Properties under test:
    is_large          — page_count > 20
    has_titles        — any slide has a non-empty title
    max_shapes_on_slide — max shape_count across slides (0 if no slides)

spec_fact_ref: FACT-FODP-001
"""

import pytest
from fodp.models import FodpDocument


def _make_slide(name: str, shape_count: int = 0, title: str = "") -> dict:
    return {
        "name": name,
        "style": "",
        "title": title,
        "text_content": "",
        "shape_count": shape_count,
    }


def _make_doc(slides: list[dict] | None = None, styles_count: int = 0) -> FodpDocument:
    slides = slides or []
    total_shapes = sum(s.get("shape_count", 0) for s in slides)
    return FodpDocument({
        "is_fodp": True,
        "page_count": len(slides),
        "pages": slides,
        "styles_count": styles_count,
        "total_shape_count": total_shapes,
    })


# ── is_large ──────────────────────────────────────────────────────────────────

class TestIsLarge:
    def test_21_slides_is_large(self):
        doc = _make_doc([_make_slide(f"S{i}") for i in range(21)])
        assert doc.is_large is True

    def test_exactly_20_not_large(self):
        doc = _make_doc([_make_slide(f"S{i}") for i in range(20)])  # not > 20
        assert doc.is_large is False

    def test_empty_not_large(self):
        doc = _make_doc([])
        assert doc.is_large is False

    def test_single_slide_not_large(self):
        doc = _make_doc([_make_slide("S1")])
        assert doc.is_large is False

    def test_30_slides_is_large(self):
        doc = _make_doc([_make_slide(f"S{i}") for i in range(30)])
        assert doc.is_large is True


# ── has_titles ────────────────────────────────────────────────────────────────

class TestHasTitles:
    def test_slide_with_title_has_titles(self):
        doc = _make_doc([_make_slide("S1", title="Introduction")])
        assert doc.has_titles is True

    def test_no_titles_empty_strings(self):
        doc = _make_doc([_make_slide("S1", title=""), _make_slide("S2", title="")])
        assert doc.has_titles is False

    def test_no_slides_no_titles(self):
        doc = _make_doc([])
        assert doc.has_titles is False

    def test_whitespace_only_title_not_counted(self):
        doc = _make_doc([_make_slide("S1", title="   ")])
        assert doc.has_titles is False

    def test_one_titled_among_untitled(self):
        doc = _make_doc([_make_slide("S1", title=""), _make_slide("S2", title="Agenda")])
        assert doc.has_titles is True

    def test_multiple_titled_slides(self):
        doc = _make_doc([_make_slide(f"S{i}", title=f"Title {i}") for i in range(5)])
        assert doc.has_titles is True


# ── max_shapes_on_slide ───────────────────────────────────────────────────────

class TestMaxShapesOnSlide:
    def test_no_slides_returns_zero(self):
        doc = _make_doc([])
        assert doc.max_shapes_on_slide == 0

    def test_single_slide_returns_shape_count(self):
        doc = _make_doc([_make_slide("S1", shape_count=5)])
        assert doc.max_shapes_on_slide == 5

    def test_max_of_multiple_slides(self):
        doc = _make_doc([
            _make_slide("S1", shape_count=3),
            _make_slide("S2", shape_count=8),
            _make_slide("S3", shape_count=2),
        ])
        assert doc.max_shapes_on_slide == 8

    def test_all_zero_slides(self):
        doc = _make_doc([_make_slide("S1", shape_count=0), _make_slide("S2", shape_count=0)])
        assert doc.max_shapes_on_slide == 0

    def test_single_large_slide(self):
        doc = _make_doc([_make_slide("S1", shape_count=50)])
        assert doc.max_shapes_on_slide == 50


# ── cross-property consistency ────────────────────────────────────────────────

class TestCrossPropertyConsistency:
    def test_large_with_titled_slides(self):
        slides = [_make_slide(f"S{i}", title=f"Title {i}") for i in range(25)]
        doc = _make_doc(slides)
        assert doc.is_large is True
        assert doc.has_titles is True

    def test_max_shapes_consistent_with_total(self):
        doc = _make_doc([_make_slide("S1", shape_count=5), _make_slide("S2", shape_count=3)])
        assert doc.max_shapes_on_slide == 5
        assert doc.total_shape_count == 8

    def test_shape_heavy_and_max_shapes(self):
        doc = _make_doc([_make_slide("S1", shape_count=10)])
        assert doc.is_shape_heavy is True
        assert doc.max_shapes_on_slide == 10
