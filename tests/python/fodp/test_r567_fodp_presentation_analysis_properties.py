"""R567: FODP presentation analysis properties — has_styles, total_shape_count, avg_shapes_per_slide.

Tests for FodpDocument presentation analysis properties added in R567.
Spec refs: SAL-FODP-00001.
"""

import pytest
from pathlib import Path

import sys
_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.models import FodpDocument

SAMPLES = Path("samples/by-format/fodp")


def _make_doc(page_count=0, styles_count=0, shape_counts=None):
    """Build a minimal FodpDocument from a dict.

    shape_counts: list of ints, one per page. Defaults to [0]*page_count.
    """
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


class TestHasStyles:
    def test_one_style_has_styles(self):
        doc = _make_doc(styles_count=1)
        assert doc.has_styles is True

    def test_multiple_styles_has_styles(self):
        doc = _make_doc(styles_count=5)
        assert doc.has_styles is True

    def test_zero_styles_no_styles(self):
        doc = _make_doc(styles_count=0)
        assert doc.has_styles is False

    def test_has_styles_type(self):
        doc = _make_doc(styles_count=0)
        assert isinstance(doc.has_styles, bool)

    def test_has_styles_consistent_with_styles_count(self):
        for n in range(5):
            doc = _make_doc(styles_count=n)
            assert doc.has_styles == (n > 0)


class TestTotalShapeCount:
    def test_no_slides_zero_shapes(self):
        doc = _make_doc(page_count=0)
        assert doc.total_shape_count == 0

    def test_one_slide_three_shapes(self):
        doc = _make_doc(page_count=1, shape_counts=[3])
        assert doc.total_shape_count == 3

    def test_two_slides_summed(self):
        doc = _make_doc(page_count=2, shape_counts=[2, 4])
        assert doc.total_shape_count == 6

    def test_zero_shapes_across_slides(self):
        doc = _make_doc(page_count=3, shape_counts=[0, 0, 0])
        assert doc.total_shape_count == 0

    def test_total_shape_count_type(self):
        doc = _make_doc(page_count=1, shape_counts=[2])
        assert isinstance(doc.total_shape_count, int)

    def test_total_shape_count_nonnegative(self):
        doc = _make_doc(page_count=0)
        assert doc.total_shape_count >= 0


class TestAvgShapesPerSlide:
    def test_zero_slides_returns_zero(self):
        doc = _make_doc(page_count=0)
        assert doc.avg_shapes_per_slide == 0.0

    def test_one_slide_two_shapes(self):
        doc = _make_doc(page_count=1, shape_counts=[2])
        assert doc.avg_shapes_per_slide == 2.0

    def test_two_slides_four_shapes(self):
        doc = _make_doc(page_count=2, shape_counts=[2, 2])
        assert doc.avg_shapes_per_slide == 2.0

    def test_fractional_average(self):
        doc = _make_doc(page_count=2, shape_counts=[1, 2])
        assert doc.avg_shapes_per_slide == 1.5

    def test_three_slides_varied(self):
        doc = _make_doc(page_count=3, shape_counts=[0, 3, 6])
        assert doc.avg_shapes_per_slide == 3.0

    def test_avg_shapes_per_slide_type(self):
        doc = _make_doc(page_count=1, shape_counts=[1])
        assert isinstance(doc.avg_shapes_per_slide, float)

    def test_avg_nonnegative(self):
        for p in range(4):
            doc = _make_doc(page_count=p, shape_counts=[1] * p)
            assert doc.avg_shapes_per_slide >= 0.0


class TestPresentationAnalysisConsistency:
    def test_has_styles_consistent(self):
        doc = _make_doc(styles_count=3)
        assert doc.has_styles
        assert doc.styles_count == 3

    def test_total_shape_count_le_expected_max(self):
        doc = _make_doc(page_count=2, shape_counts=[3, 5])
        assert doc.total_shape_count == 8
        assert doc.avg_shapes_per_slide == 4.0

    def test_from_file_minimal(self):
        doc = FodpDocument.from_file(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(doc.has_styles, bool)
        assert isinstance(doc.total_shape_count, int)
        assert isinstance(doc.avg_shapes_per_slide, float)
