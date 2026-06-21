"""Tests for fodp_is_single_nonempty_slide and fodp_avg_words_per_slide (Sprint 79, R289)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodp.fodp_codec import fodp_is_single_nonempty_slide, fodp_avg_words_per_slide

FODP = _REPO / "samples" / "by-format" / "fodp"


@pytest.fixture
def minimal():
    return FODP / "minimal-presentation.fodp"


@pytest.fixture
def two_slides():
    return FODP / "two-slides-basic.fodp"


@pytest.fixture
def title_only():
    return FODP / "title-only.fodp"


def test_is_single_nonempty_slide_minimal_true(minimal):
    assert fodp_is_single_nonempty_slide(minimal) is True


def test_is_single_nonempty_slide_two_slides_false(two_slides):
    assert fodp_is_single_nonempty_slide(two_slides) is False


def test_is_single_nonempty_slide_empty_false(title_only):
    assert fodp_is_single_nonempty_slide(title_only) is False


def test_is_single_nonempty_slide_returns_bool(minimal):
    assert isinstance(fodp_is_single_nonempty_slide(minimal), bool)


def test_avg_words_per_slide_minimal(minimal):
    assert abs(fodp_avg_words_per_slide(minimal) - 1.0) < 0.01


def test_avg_words_per_slide_two_slides(two_slides):
    assert abs(fodp_avg_words_per_slide(two_slides) - 2.5) < 0.01


def test_avg_words_per_slide_empty(title_only):
    assert abs(fodp_avg_words_per_slide(title_only) - 0.0) < 0.01


def test_avg_words_per_slide_returns_float(minimal):
    assert isinstance(fodp_avg_words_per_slide(minimal), float)


def test_avg_words_per_slide_nonnegative(two_slides):
    assert fodp_avg_words_per_slide(two_slides) >= 0.0


def test_is_single_nonempty_consistent_with_nonempty_count(minimal):
    from fodp.fodp_codec import fodp_nonempty_slide_count
    assert fodp_is_single_nonempty_slide(minimal) == (fodp_nonempty_slide_count(minimal) == 1)
