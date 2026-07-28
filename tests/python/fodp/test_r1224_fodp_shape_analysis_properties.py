"""R1224: FODP shape analysis properties — has_shapes, is_shape_heavy, is_single_slide_with_shapes.

Tests for FodpDocument shape analysis properties added in R1224.
Spec refs: SAL-FODP-00001 (office:document presentation structure).
"""

from __future__ import annotations

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.models import FodpDocument

SAMPLES = Path("samples/by-format/fodp")


def _make_doc(page_count: int = 0, styles_count: int = 0, shape_counts: list[int] | None = None) -> FodpDocument:
    """Build a minimal FodpDocument from stub data."""
    if shape_counts is None:
        shape_counts = [0] * page_count
    pages = [
        {"name": f"Slide{i}", "shape_count": shape_counts[i], "text_content": [], "title": ""}
        for i in range(page_count)
    ]
    return FodpDocument({
        "is_fodp": True,
        "page_count": page_count,
        "pages": pages,
        "styles_count": styles_count,
    })


class TestHasShapes:
    def test_no_slides_no_shapes(self):
        doc = _make_doc(page_count=0)
        assert doc.has_shapes is False

    def test_slides_with_zero_shapes(self):
        doc = _make_doc(page_count=2, shape_counts=[0, 0])
        assert doc.has_shapes is False

    def test_one_shape_has_shapes(self):
        doc = _make_doc(page_count=1, shape_counts=[1])
        assert doc.has_shapes is True

    def test_multiple_shapes_has_shapes(self):
        doc = _make_doc(page_count=3, shape_counts=[2, 0, 5])
        assert doc.has_shapes is True

    def test_returns_bool(self):
        doc = _make_doc(page_count=1, shape_counts=[3])
        assert isinstance(doc.has_shapes, bool)

    def test_from_file(self):
        for p in sorted(SAMPLES.glob("*.fodp"))[:2]:
            doc = FodpDocument.from_file(p)
            assert isinstance(doc.has_shapes, bool)


class TestIsShapeHeavy:
    def test_empty_not_shape_heavy(self):
        doc = _make_doc(page_count=0)
        assert doc.is_shape_heavy is False

    def test_five_per_slide_not_heavy(self):
        """avg_shapes_per_slide == 5.0, threshold is > 5."""
        doc = _make_doc(page_count=1, shape_counts=[5])
        assert doc.is_shape_heavy is False

    def test_six_per_slide_is_heavy(self):
        doc = _make_doc(page_count=1, shape_counts=[6])
        assert doc.is_shape_heavy is True

    def test_avg_crosses_threshold(self):
        """3 slides with shapes [3, 6, 9] → avg = 6.0 > 5."""
        doc = _make_doc(page_count=3, shape_counts=[3, 6, 9])
        assert doc.is_shape_heavy is True

    def test_avg_below_threshold(self):
        """3 slides with shapes [2, 2, 2] → avg = 2.0 ≤ 5."""
        doc = _make_doc(page_count=3, shape_counts=[2, 2, 2])
        assert doc.is_shape_heavy is False

    def test_returns_bool(self):
        doc = _make_doc(page_count=1, shape_counts=[3])
        assert isinstance(doc.is_shape_heavy, bool)


class TestIsSingleSlideWithShapes:
    def test_no_slides_false(self):
        doc = _make_doc(page_count=0)
        assert doc.is_single_slide_with_shapes is False

    def test_single_slide_no_shapes_false(self):
        doc = _make_doc(page_count=1, shape_counts=[0])
        assert doc.is_single_slide_with_shapes is False

    def test_single_slide_with_shape_true(self):
        doc = _make_doc(page_count=1, shape_counts=[1])
        assert doc.is_single_slide_with_shapes is True

    def test_multi_slide_with_shapes_false(self):
        doc = _make_doc(page_count=2, shape_counts=[3, 2])
        assert doc.is_single_slide_with_shapes is False

    def test_multi_slide_no_shapes_false(self):
        doc = _make_doc(page_count=2, shape_counts=[0, 0])
        assert doc.is_single_slide_with_shapes is False

    def test_returns_bool(self):
        doc = _make_doc(page_count=1, shape_counts=[5])
        assert isinstance(doc.is_single_slide_with_shapes, bool)

    def test_from_file(self):
        for p in sorted(SAMPLES.glob("*.fodp"))[:2]:
            doc = FodpDocument.from_file(p)
            assert isinstance(doc.is_single_slide_with_shapes, bool)
