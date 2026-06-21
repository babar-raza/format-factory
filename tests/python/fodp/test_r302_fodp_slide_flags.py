"""Tests for fodp_slide_count_is_even and fodp_has_multiple_slides (Sprint r302)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_slide_count_is_even, fodp_has_multiple_slides

_FODP = _REPO / "samples" / "by-format" / "fodp"


class TestFodpSlideCountIsEven:
    """Tests for fodp_slide_count_is_even."""

    def test_minimal_one_slide_is_odd(self):
        """minimal-presentation.fodp has 1 slide (odd) → False."""
        result = fodp_slide_count_is_even(_FODP / "minimal-presentation.fodp")
        assert result is False

    def test_title_only_zero_slides_is_even(self):
        """title-only.fodp has 0 slides (even) → True."""
        result = fodp_slide_count_is_even(_FODP / "title-only.fodp")
        assert result is True

    def test_two_slides_is_even(self):
        """two-slides-basic.fodp has 2 slides (even) → True."""
        result = fodp_slide_count_is_even(_FODP / "two-slides-basic.fodp")
        assert result is True

    def test_returns_bool(self):
        result = fodp_slide_count_is_even(_FODP / "minimal-presentation.fodp")
        assert isinstance(result, bool)

    def test_even_files_return_true(self):
        for f in ["title-only.fodp", "two-slides-basic.fodp"]:
            assert fodp_slide_count_is_even(_FODP / f) is True

    def test_minimal_false_two_slides_true(self):
        r1 = fodp_slide_count_is_even(_FODP / "minimal-presentation.fodp")
        r2 = fodp_slide_count_is_even(_FODP / "two-slides-basic.fodp")
        assert r1 is False and r2 is True


class TestFodpHasMultipleSlides:
    """Tests for fodp_has_multiple_slides."""

    def test_minimal_has_one_slide_not_multiple(self):
        """minimal-presentation.fodp has 1 slide → False."""
        result = fodp_has_multiple_slides(_FODP / "minimal-presentation.fodp")
        assert result is False

    def test_title_only_zero_slides_not_multiple(self):
        """title-only.fodp has 0 slides → False."""
        result = fodp_has_multiple_slides(_FODP / "title-only.fodp")
        assert result is False

    def test_two_slides_has_multiple(self):
        """two-slides-basic.fodp has 2 slides → True."""
        result = fodp_has_multiple_slides(_FODP / "two-slides-basic.fodp")
        assert result is True

    def test_returns_bool(self):
        result = fodp_has_multiple_slides(_FODP / "two-slides-basic.fodp")
        assert isinstance(result, bool)

    def test_single_slide_files_return_false(self):
        for f in ["minimal-presentation.fodp", "title-only.fodp"]:
            assert fodp_has_multiple_slides(_FODP / f) is False

    def test_two_slides_true_minimal_false(self):
        r1 = fodp_has_multiple_slides(_FODP / "minimal-presentation.fodp")
        r2 = fodp_has_multiple_slides(_FODP / "two-slides-basic.fodp")
        assert r1 is False and r2 is True
