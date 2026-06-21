"""Tests for ABW Sprint 57 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_CHARS_PE-001   (Abw Chars Per Word)
  GAP-ABW-FOSS-ABW_HAS_MULT-001   (Abw Has Multi Para)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_chars_per_word, abw_has_multi_para

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwCharsPerWord:
    def test_return_type(self):
        assert isinstance(abw_chars_per_word(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_chars_per_word(_EMPTY) == 0.0

    def test_exact_5_for_minimal(self):
        assert abw_chars_per_word(_MINIMAL) == 5.0

    def test_exact_8_25_for_two_paragraphs(self):
        assert abw_chars_per_word(_TWO_PARA) == 8.25

    def test_nonnegative(self):
        assert abw_chars_per_word(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_chars_per_word(_MINIMAL) == abw_chars_per_word(_MINIMAL)


class TestAbwHasMultiPara:
    def test_return_type(self):
        assert isinstance(abw_has_multi_para(_MINIMAL), bool)

    def test_false_for_empty(self):
        assert abw_has_multi_para(_EMPTY) is False

    def test_false_for_minimal(self):
        assert abw_has_multi_para(_MINIMAL) is False

    def test_true_for_two_paragraphs(self):
        assert abw_has_multi_para(_TWO_PARA) is True

    def test_consistent_across_calls(self):
        assert abw_has_multi_para(_MINIMAL) == abw_has_multi_para(_MINIMAL)
