"""Tests for fodp_total_shape_count() — total shape count across all slides."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_total_shape_count, fodp_slide_shape_counts

SAMPLES = _REPO / "samples" / "by-format" / "fodp"


class TestFodpTotalShapeCount:
    def test_minimal_presentation(self):
        result = fodp_total_shape_count(SAMPLES / "minimal-presentation.fodp")
        assert result == 1

    def test_title_only_zero(self):
        result = fodp_total_shape_count(SAMPLES / "title-only.fodp")
        assert result == 0

    def test_two_slides_basic(self):
        result = fodp_total_shape_count(SAMPLES / "two-slides-basic.fodp")
        assert result == 3  # 2 + 1

    def test_returns_int(self):
        result = fodp_total_shape_count(SAMPLES / "minimal-presentation.fodp")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fodp_total_shape_count(SAMPLES / "title-only.fodp")
        assert result >= 0

    def test_equals_sum_of_per_slide(self):
        for sample in SAMPLES.glob("*.fodp"):
            total = fodp_total_shape_count(sample)
            per_slide = fodp_slide_shape_counts(sample)
            assert total == sum(per_slide), f"Mismatch for {sample.name}"

    def test_importable_from_init(self):
        from src.python.fodp import fodp_total_shape_count as fn
        assert callable(fn)

    def test_in_all_list(self):
        from src.python.fodp import __all__
        assert "fodp_total_shape_count" in __all__
