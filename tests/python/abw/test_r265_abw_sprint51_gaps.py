"""Tests for ABW Sprint 51 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_ALPHA_CH-001  (Abw Alpha Char Count)
  GAP-ABW-FOSS-ABW_SPACE_CO-001  (Abw Space Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_alpha_char_count, abw_space_count

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_EMPTY = str(_DIR / "empty-section.abw")
_TWO = str(_DIR / "two-paragraphs.abw")


class TestAbwAlphaCharCount:
    def test_return_type(self):
        assert isinstance(abw_alpha_char_count(_MINIMAL), int)

    def test_exact_5_for_minimal(self):
        assert abw_alpha_char_count(_MINIMAL) == 5

    def test_zero_for_empty(self):
        assert abw_alpha_char_count(_EMPTY) == 0

    def test_exact_29_for_two_paragraphs(self):
        assert abw_alpha_char_count(_TWO) == 29

    def test_nonnegative(self):
        assert abw_alpha_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_alpha_char_count(_MINIMAL) == abw_alpha_char_count(_MINIMAL)


class TestAbwSpaceCount:
    def test_return_type(self):
        assert isinstance(abw_space_count(_MINIMAL), int)

    def test_zero_for_minimal(self):
        assert abw_space_count(_MINIMAL) == 0

    def test_zero_for_empty(self):
        assert abw_space_count(_EMPTY) == 0

    def test_exact_2_for_two_paragraphs(self):
        assert abw_space_count(_TWO) == 2

    def test_nonnegative(self):
        assert abw_space_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_space_count(_MINIMAL) == abw_space_count(_MINIMAL)
