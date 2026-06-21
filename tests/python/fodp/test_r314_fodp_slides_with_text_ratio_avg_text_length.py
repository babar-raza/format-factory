"""Tests for fodp_slides_with_text_ratio and fodp_avg_text_length_per_slide (Sprint 104, R314)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_slides_with_text_ratio, fodp_avg_text_length_per_slide

FODP = _REPO / "samples" / "by-format" / "fodp"


def test_text_ratio_minimal():
    assert abs(fodp_slides_with_text_ratio(FODP / "minimal-presentation.fodp") - 1.0) < 0.001


def test_text_ratio_title_only():
    assert abs(fodp_slides_with_text_ratio(FODP / "title-only.fodp") - 0.0) < 0.001


def test_text_ratio_two_slides():
    assert abs(fodp_slides_with_text_ratio(FODP / "two-slides-basic.fodp") - 1.0) < 0.001


def test_text_ratio_returns_float():
    assert isinstance(fodp_slides_with_text_ratio(FODP / "minimal-presentation.fodp"), float)


def test_text_ratio_bounded():
    r = fodp_slides_with_text_ratio(FODP / "minimal-presentation.fodp")
    assert 0.0 <= r <= 1.0


def test_avg_text_length_minimal():
    assert abs(fodp_avg_text_length_per_slide(FODP / "minimal-presentation.fodp") - 5.0) < 0.01


def test_avg_text_length_title_only():
    assert abs(fodp_avg_text_length_per_slide(FODP / "title-only.fodp") - 0.0) < 0.01


def test_avg_text_length_two_slides():
    assert abs(fodp_avg_text_length_per_slide(FODP / "two-slides-basic.fodp") - 21.0) < 0.01


def test_avg_text_length_returns_float():
    assert isinstance(fodp_avg_text_length_per_slide(FODP / "minimal-presentation.fodp"), float)


def test_avg_text_length_nonnegative():
    assert fodp_avg_text_length_per_slide(FODP / "title-only.fodp") >= 0.0
