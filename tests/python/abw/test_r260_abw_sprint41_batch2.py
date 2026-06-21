"""Tests for ABW Sprint 41 batch 2 gap closure.

Closes:
  GAP-ABW-FOSS-ABW_CAPITAL_-001  (Abw Capital Word Count)
  GAP-ABW-FOSS-ABW_AVG_PARA-001  (Abw Avg Paragraph Words)
  GAP-ABW-FOSS-ABW_TEXT_DEN-001  (Abw Text Density)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import abw_avg_paragraph_words, abw_capital_word_count, abw_text_density

_DIR = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARA = str(_DIR / "two-paragraphs.abw")


class TestAbwCapitalWordCount:
    def test_return_type(self):
        assert isinstance(abw_capital_word_count(_MINIMAL), int)

    def test_exact_1_for_minimal(self):
        assert abw_capital_word_count(_MINIMAL) == 1

    def test_exact_2_for_two_paragraphs(self):
        assert abw_capital_word_count(_TWO_PARA) == 2

    def test_nonnegative(self):
        assert abw_capital_word_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_capital_word_count(_MINIMAL) == abw_capital_word_count(_MINIMAL)


class TestAbwAvgParagraphWords:
    def test_return_type(self):
        assert isinstance(abw_avg_paragraph_words(_MINIMAL), float)

    def test_exact_1_0_for_minimal(self):
        assert abw_avg_paragraph_words(_MINIMAL) == 1.0

    def test_exact_2_0_for_two_paragraphs(self):
        assert abw_avg_paragraph_words(_TWO_PARA) == 2.0

    def test_positive(self):
        assert abw_avg_paragraph_words(_MINIMAL) > 0

    def test_consistent_across_calls(self):
        assert abw_avg_paragraph_words(_MINIMAL) == abw_avg_paragraph_words(_MINIMAL)


class TestAbwTextDensity:
    def test_return_type(self):
        assert isinstance(abw_text_density(_MINIMAL), float)

    def test_exact_1_0_for_minimal(self):
        assert abw_text_density(_MINIMAL) == 1.0

    def test_nonnegative(self):
        assert abw_text_density(_MINIMAL) >= 0.0

    def test_at_most_1(self):
        assert abw_text_density(_MINIMAL) <= 1.0

    def test_consistent_across_calls(self):
        assert abw_text_density(_MINIMAL) == abw_text_density(_MINIMAL)
