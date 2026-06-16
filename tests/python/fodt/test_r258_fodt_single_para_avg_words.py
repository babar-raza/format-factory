"""Tests for fodt_is_single_paragraph and fodt_avg_words_per_paragraph (Sprint 48)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.fodt import fodt_is_single_paragraph, fodt_avg_words_per_paragraph

_DIR = _REPO / "samples" / "by-format" / "fodt"
_MINIMAL = str(_DIR / "minimal-document.fodt")          # 1 para, 2 words
_HEADINGS = str(_DIR / "headings-and-paragraphs.fodt")  # 4 paras, 44 words
_LIST = str(_DIR / "list-basic.fodt")                   # 2 paras, 6 words
_TABLE = str(_DIR / "table-basic.fodt")                 # 2 paras, 7 words


class TestFodtIsSingleParagraph:
    def test_return_type(self):
        assert isinstance(fodt_is_single_paragraph(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-document.fodt has exactly 1 paragraph
        assert fodt_is_single_paragraph(_MINIMAL) is True

    def test_false_for_headings(self):
        # headings-and-paragraphs.fodt has 4 paragraphs
        assert fodt_is_single_paragraph(_HEADINGS) is False

    def test_false_for_list(self):
        # list-basic.fodt has 2 paragraphs
        assert fodt_is_single_paragraph(_LIST) is False

    def test_consistent_across_calls(self):
        assert fodt_is_single_paragraph(_MINIMAL) == fodt_is_single_paragraph(_MINIMAL)

    def test_single_para_implies_count_1(self):
        from src.python.fodt import fodt_paragraph_count
        if fodt_is_single_paragraph(_MINIMAL):
            assert fodt_paragraph_count(_MINIMAL) == 1


class TestFodtAvgWordsPerParagraph:
    def test_return_type(self):
        assert isinstance(fodt_avg_words_per_paragraph(_MINIMAL), float)

    def test_exact_2_for_minimal(self):
        # minimal-document.fodt: 2 words / 1 para = 2.0
        assert fodt_avg_words_per_paragraph(_MINIMAL) == 2.0

    def test_exact_11_for_headings(self):
        # headings-and-paragraphs.fodt: 44 words / 4 paras = 11.0
        assert fodt_avg_words_per_paragraph(_HEADINGS) == 11.0

    def test_exact_3_for_list(self):
        # list-basic.fodt: 6 words / 2 paras = 3.0
        assert fodt_avg_words_per_paragraph(_LIST) == 3.0

    def test_nonnegative(self):
        assert fodt_avg_words_per_paragraph(_MINIMAL) >= 0.0

    def test_consistent_across_calls(self):
        assert fodt_avg_words_per_paragraph(_MINIMAL) == fodt_avg_words_per_paragraph(_MINIMAL)
