"""Tests for fodp_chars_per_shape and fodp_total_chars_per_slide (Sprint 89, R299)."""
import sys
from pathlib import Path
import pytest

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodp.fodp_codec import fodp_chars_per_shape, fodp_total_chars_per_slide

FODP = _REPO / "samples" / "by-format" / "fodp"


@pytest.fixture
def minimal():
    return FODP / "minimal-presentation.fodp"


@pytest.fixture
def title_only():
    return FODP / "title-only.fodp"


@pytest.fixture
def two_slides():
    return FODP / "two-slides-basic.fodp"


def test_chars_per_shape_minimal(minimal):
    assert abs(fodp_chars_per_shape(minimal) - 5.0) < 0.01


def test_chars_per_shape_title_only(title_only):
    assert abs(fodp_chars_per_shape(title_only) - 0.0) < 0.01


def test_chars_per_shape_two_slides(two_slides):
    assert fodp_chars_per_shape(two_slides) > 10.0


def test_chars_per_shape_returns_float(minimal):
    assert isinstance(fodp_chars_per_shape(minimal), float)


def test_chars_per_shape_nonnegative(title_only):
    assert fodp_chars_per_shape(title_only) >= 0.0


def test_total_chars_per_slide_minimal(minimal):
    assert abs(fodp_total_chars_per_slide(minimal) - 5.0) < 0.01


def test_total_chars_per_slide_title_only(title_only):
    assert abs(fodp_total_chars_per_slide(title_only) - 0.0) < 0.01


def test_total_chars_per_slide_two_slides(two_slides):
    assert abs(fodp_total_chars_per_slide(two_slides) - 21.5) < 0.01


def test_total_chars_per_slide_returns_float(minimal):
    assert isinstance(fodp_total_chars_per_slide(minimal), float)


def test_total_chars_per_slide_nonnegative(title_only):
    assert fodp_total_chars_per_slide(title_only) >= 0.0
