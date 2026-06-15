"""Tests for fodp_slide_count().

Sprint: product-deepening-rnext87
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_slide_count

FODP_SAMPLES = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideCount:
    def test_import(self):
        assert callable(fodp_slide_count)

    def test_minimal_presentation_has_one_slide(self):
        assert fodp_slide_count(FODP_SAMPLES / "minimal-presentation.fodp") == 1

    def test_title_only_has_zero_slides(self):
        assert fodp_slide_count(FODP_SAMPLES / "title-only.fodp") == 0

    def test_two_slides_basic(self):
        assert fodp_slide_count(FODP_SAMPLES / "two-slides-basic.fodp") == 2

    def test_returns_int(self):
        result = fodp_slide_count(FODP_SAMPLES / "minimal-presentation.fodp")
        assert isinstance(result, int)

    def test_nonnegative(self):
        for sample in FODP_SAMPLES.iterdir():
            if sample.suffix == ".fodp":
                assert fodp_slide_count(sample) >= 0
