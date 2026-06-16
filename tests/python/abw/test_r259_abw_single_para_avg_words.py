"""Tests for abw_is_single_paragraph and abw_avg_words_per_paragraph (Sprint 49)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_is_single_paragraph, abw_avg_words_per_paragraph

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")   # 1 para, 1 word
_TWO = str(_DIR / "two-paragraphs.abw")          # 2 paras, 4 words
_EMPTY = str(_DIR / "empty-section.abw")         # 0 paras, 0 words


class TestAbwIsSingleParagraph:
    def test_return_type(self):
        assert isinstance(abw_is_single_paragraph(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-document.abw has exactly 1 paragraph
        assert abw_is_single_paragraph(_MINIMAL) is True

    def test_false_for_two_paragraphs(self):
        # two-paragraphs.abw has 2 paragraphs
        assert abw_is_single_paragraph(_TWO) is False

    def test_false_for_empty(self):
        # empty-section.abw has 0 paragraphs
        assert abw_is_single_paragraph(_EMPTY) is False

    def test_consistent_across_calls(self):
        assert abw_is_single_paragraph(_MINIMAL) == abw_is_single_paragraph(_MINIMAL)

    def test_single_para_implies_count_1(self):
        from src.python.abw import abw_paragraph_count
        if abw_is_single_paragraph(_MINIMAL):
            assert abw_paragraph_count(_MINIMAL) == 1


class TestAbwAvgWordsPerParagraph:
    def test_return_type(self):
        assert isinstance(abw_avg_words_per_paragraph(_MINIMAL), float)

    def test_exact_1_for_minimal(self):
        # minimal-document.abw: 1 word / 1 para = 1.0
        assert abw_avg_words_per_paragraph(_MINIMAL) == 1.0

    def test_exact_2_for_two_paragraphs(self):
        # two-paragraphs.abw: 4 words / 2 paras = 2.0
        assert abw_avg_words_per_paragraph(_TWO) == 2.0

    def test_zero_for_empty(self):
        # empty-section.abw: 0 paras → 0.0
        assert abw_avg_words_per_paragraph(_EMPTY) == 0.0

    def test_nonnegative(self):
        assert abw_avg_words_per_paragraph(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert abw_avg_words_per_paragraph(_MINIMAL) == abw_avg_words_per_paragraph(_MINIMAL)
