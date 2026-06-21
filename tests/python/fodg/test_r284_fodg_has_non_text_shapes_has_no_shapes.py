"""Tests for fodg_has_non_text_shapes and fodg_has_no_shapes (Sprint 74)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodg.fodg_codec import fodg_has_non_text_shapes, fodg_has_no_shapes

FODG = _REPO / "samples" / "by-format" / "fodg"


# --- fodg_has_non_text_shapes ---

def test_has_non_text_shapes_minimal_false():
    assert fodg_has_non_text_shapes(FODG / "minimal-drawing.fodg") is False


def test_has_non_text_shapes_shapes_basic_true():
    assert fodg_has_non_text_shapes(FODG / "shapes-basic.fodg") is True


def test_has_non_text_shapes_empty_page_false():
    assert fodg_has_non_text_shapes(FODG / "empty-page.fodg") is False


def test_has_non_text_shapes_returns_bool():
    assert isinstance(fodg_has_non_text_shapes(FODG / "minimal-drawing.fodg"), bool)


def test_has_non_text_shapes_differs_from_has_no_shapes():
    # shapes-basic has non-text shapes but is NOT has_no_shapes
    assert fodg_has_non_text_shapes(FODG / "shapes-basic.fodg") is True
    assert fodg_has_no_shapes(FODG / "shapes-basic.fodg") is False


# --- fodg_has_no_shapes ---

def test_has_no_shapes_minimal_false():
    assert fodg_has_no_shapes(FODG / "minimal-drawing.fodg") is False


def test_has_no_shapes_shapes_basic_false():
    assert fodg_has_no_shapes(FODG / "shapes-basic.fodg") is False


def test_has_no_shapes_empty_page_true():
    assert fodg_has_no_shapes(FODG / "empty-page.fodg") is True


def test_has_no_shapes_returns_bool():
    assert isinstance(fodg_has_no_shapes(FODG / "empty-page.fodg"), bool)


def test_has_no_shapes_empty_implies_no_non_text():
    # empty-page has no shapes so has_non_text_shapes must also be False
    assert fodg_has_no_shapes(FODG / "empty-page.fodg") is True
    assert fodg_has_non_text_shapes(FODG / "empty-page.fodg") is False
