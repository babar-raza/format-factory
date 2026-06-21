"""Tests for FODG Sprint 57 gap closure.

Closes:
  GAP-FODG-FOSS-FODG_WORD_CO-001   (Fodg Word Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodg import fodg_word_count

_DIR = _REPO / "samples" / "by-format" / "fodg"
_EMPTY = str(_DIR / "empty-page.fodg")
_MINIMAL = str(_DIR / "minimal-drawing.fodg")
_SHAPES = str(_DIR / "shapes-basic.fodg")


class TestFodgWordCount:
    def test_return_type(self):
        assert isinstance(fodg_word_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert fodg_word_count(_EMPTY) == 0

    def test_zero_for_minimal(self):
        assert fodg_word_count(_MINIMAL) == 0

    def test_zero_for_shapes(self):
        assert fodg_word_count(_SHAPES) == 0

    def test_nonnegative(self):
        assert fodg_word_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert fodg_word_count(_MINIMAL) == fodg_word_count(_MINIMAL)
