"""Tests for fodp_all_slides_have_text and fodp_max_title_length (Sprint 35)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodp import fodp_all_slides_have_text, fodp_max_title_length

_SAMPLES = _REPO / "samples" / "by-format" / "fodp"
_MINIMAL = str(_SAMPLES / "minimal-presentation.fodp")  # 1 slide "Hello" -> all_text=True
_TITLE_ONLY = str(_SAMPLES / "title-only.fodp")         # 0 slides -> all_text=False
_TWO_SLIDES = str(_SAMPLES / "two-slides-basic.fodp")   # 2 slides with text -> all_text=True


class TestFodpAllSlidesHaveText:
    def test_return_type(self):
        result = fodp_all_slides_have_text(_MINIMAL)
        assert isinstance(result, bool)

    def test_true_for_minimal_with_text(self):
        assert fodp_all_slides_have_text(_MINIMAL) is True

    def test_false_for_empty_presentation(self):
        assert fodp_all_slides_have_text(_TITLE_ONLY) is False

    def test_true_for_two_slides_with_text(self):
        assert fodp_all_slides_have_text(_TWO_SLIDES) is True

    def test_consistent_across_calls(self):
        assert fodp_all_slides_have_text(_MINIMAL) == fodp_all_slides_have_text(_MINIMAL)


class TestFodpMaxTitleLength:
    def test_return_type(self):
        result = fodp_max_title_length(_MINIMAL)
        assert isinstance(result, int)

    def test_exact_for_minimal(self):
        # minimal-presentation.fodp title "Hello" -> len=5
        assert fodp_max_title_length(_MINIMAL) == 5

    def test_zero_for_empty(self):
        assert fodp_max_title_length(_TITLE_ONLY) == 0

    def test_exact_for_two_slides(self):
        # titles: "Introduction"(12), "Conclusion"(10) -> max=12
        assert fodp_max_title_length(_TWO_SLIDES) == 12

    def test_nonnegative(self):
        assert fodp_max_title_length(_MINIMAL) >= 0
