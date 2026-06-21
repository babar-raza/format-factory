"""Tests for fodg_text_percentage and fodg_non_text_shape_percentage (Sprint 107, R317)."""
import sys
from pathlib import Path

_REPO = Path(__file__).parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fodg.fodg_codec import fodg_text_percentage, fodg_non_text_shape_percentage

FODG = _REPO / "samples" / "by-format" / "fodg"


def test_text_pct_minimal():
    assert abs(fodg_text_percentage(FODG / "minimal-drawing.fodg") - 100.0) < 0.1


def test_text_pct_empty():
    assert abs(fodg_text_percentage(FODG / "empty-page.fodg") - 0.0) < 0.1


def test_text_pct_shapes():
    assert abs(fodg_text_percentage(FODG / "shapes-basic.fodg") - 66.67) < 0.1


def test_text_pct_returns_float():
    assert isinstance(fodg_text_percentage(FODG / "minimal-drawing.fodg"), float)


def test_text_pct_bounded():
    pct = fodg_text_percentage(FODG / "minimal-drawing.fodg")
    assert 0.0 <= pct <= 100.0


def test_non_text_pct_minimal():
    assert abs(fodg_non_text_shape_percentage(FODG / "minimal-drawing.fodg") - 0.0) < 0.1


def test_non_text_pct_empty():
    assert abs(fodg_non_text_shape_percentage(FODG / "empty-page.fodg") - 0.0) < 0.1


def test_non_text_pct_shapes():
    assert abs(fodg_non_text_shape_percentage(FODG / "shapes-basic.fodg") - 66.67) < 0.1


def test_non_text_pct_returns_float():
    assert isinstance(fodg_non_text_shape_percentage(FODG / "minimal-drawing.fodg"), float)


def test_non_text_pct_nonnegative():
    assert fodg_non_text_shape_percentage(FODG / "shapes-basic.fodg") >= 0.0
