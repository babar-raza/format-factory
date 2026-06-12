"""
tests/python/fodp/test_r185_fodp_slide_shape_counts.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT55-001
Tests for fodp_slide_shape_counts() — shape count per slide.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_slide_shape_counts

SAMPLES = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideShapeCounts:
    def test_minimal_presentation_one_shape(self):
        result = fodp_slide_shape_counts(SAMPLES / "minimal-presentation.fodp")
        assert result == [1]

    def test_title_only_empty_list(self):
        result = fodp_slide_shape_counts(SAMPLES / "title-only.fodp")
        assert result == []

    def test_two_slides_basic(self):
        result = fodp_slide_shape_counts(SAMPLES / "two-slides-basic.fodp")
        assert result == [2, 1]

    def test_returns_list(self):
        result = fodp_slide_shape_counts(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(result, list)

    def test_list_elements_are_ints(self):
        result = fodp_slide_shape_counts(SAMPLES / "two-slides-basic.fodp")
        assert all(isinstance(x, int) for x in result)

    def test_exported_from_init(self):
        from src.python.fodp import fodp_slide_shape_counts as fn
        result = fn(SAMPLES / "two-slides-basic.fodp")
        assert result == [2, 1]
