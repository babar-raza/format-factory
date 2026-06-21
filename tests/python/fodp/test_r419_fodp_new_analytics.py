"""Tests for fodp_slide_count_squared and fodp_total_shapes_plus_slide_count."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
if str(_REPO) not in sys.path:
    sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import (
    fodp_slide_count_squared,
    fodp_total_shapes_plus_slide_count,
    fodp_slide_count,
    fodp_total_shape_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
_TITLE = _SAMPLES / "title-only.fodp"
_MULTI = _SAMPLES / "two-slides-basic.fodp"


class TestFodpSlideCountSquared:
    def test_returns_int(self):
        assert isinstance(fodp_slide_count_squared(_TITLE), int)

    def test_matches_formula(self):
        sc = fodp_slide_count(_TITLE)
        assert fodp_slide_count_squared(_TITLE) == sc * sc

    def test_nonnegative(self):
        assert fodp_slide_count_squared(_TITLE) >= 0

    def test_multi_slide(self):
        sc = fodp_slide_count(_MULTI)
        assert fodp_slide_count_squared(_MULTI) == sc * sc

    def test_consistent(self):
        assert fodp_slide_count_squared(_TITLE) == fodp_slide_count_squared(_TITLE)


class TestFodpTotalShapesPlusSlideCount:
    def test_returns_int(self):
        assert isinstance(fodp_total_shapes_plus_slide_count(_TITLE), int)

    def test_matches_sum(self):
        shapes = fodp_total_shape_count(_TITLE)
        slides = fodp_slide_count(_TITLE)
        assert fodp_total_shapes_plus_slide_count(_TITLE) == shapes + slides

    def test_nonnegative(self):
        assert fodp_total_shapes_plus_slide_count(_TITLE) >= 0

    def test_multi_slide(self):
        shapes = fodp_total_shape_count(_MULTI)
        slides = fodp_slide_count(_MULTI)
        assert fodp_total_shapes_plus_slide_count(_MULTI) == shapes + slides

    def test_consistent(self):
        assert fodp_total_shapes_plus_slide_count(_MULTI) == fodp_total_shapes_plus_slide_count(_MULTI)
