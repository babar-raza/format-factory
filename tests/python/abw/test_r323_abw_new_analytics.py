"""
test_r323_abw_new_analytics.py
Sprint 59 — 5 new ABW analytics functions.
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw import (
    abw_file_size_bytes,
    abw_max_word_count_para,
    abw_min_word_count_para,
    abw_avg_words_per_paragraph,
    abw_digit_char_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "abw"
_MINIMAL = str(_SAMPLES / "minimal-document.abw")
_TWO = str(_SAMPLES / "two-paragraphs.abw")
_EMPTY = str(_SAMPLES / "empty-section.abw")


# --- abw_file_size_bytes ---

class TestAbwFileSizeBytes:
    def test_minimal_positive(self):
        assert abw_file_size_bytes(_MINIMAL) > 0

    def test_two_positive(self):
        assert abw_file_size_bytes(_TWO) > 0

    def test_empty_positive(self):
        assert abw_file_size_bytes(_EMPTY) > 0

    def test_returns_int(self):
        assert isinstance(abw_file_size_bytes(_MINIMAL), int)

    def test_reasonable_size(self):
        assert abw_file_size_bytes(_MINIMAL) >= 50


# --- abw_max_word_count_para ---

class TestAbwMaxWordCountPara:
    def test_returns_int(self):
        assert isinstance(abw_max_word_count_para(_TWO), int)

    def test_two_non_negative(self):
        assert abw_max_word_count_para(_TWO) >= 0

    def test_minimal_non_negative(self):
        assert abw_max_word_count_para(_MINIMAL) >= 0

    def test_max_ge_min(self):
        assert abw_max_word_count_para(_TWO) >= abw_min_word_count_para(_TWO)

    def test_empty_zero(self):
        assert abw_max_word_count_para(_EMPTY) >= 0


# --- abw_min_word_count_para ---

class TestAbwMinWordCountPara:
    def test_returns_int(self):
        assert isinstance(abw_min_word_count_para(_TWO), int)

    def test_two_non_negative(self):
        assert abw_min_word_count_para(_TWO) >= 0

    def test_minimal_non_negative(self):
        assert abw_min_word_count_para(_MINIMAL) >= 0

    def test_min_le_max(self):
        assert abw_min_word_count_para(_TWO) <= abw_max_word_count_para(_TWO)

    def test_empty_zero(self):
        assert abw_min_word_count_para(_EMPTY) >= 0


# --- abw_avg_words_per_paragraph ---

class TestAbwAvgWordsPerParagraph:
    def test_returns_float(self):
        assert isinstance(abw_avg_words_per_paragraph(_TWO), float)

    def test_two_non_negative(self):
        assert abw_avg_words_per_paragraph(_TWO) >= 0.0

    def test_minimal_non_negative(self):
        assert abw_avg_words_per_paragraph(_MINIMAL) >= 0.0

    def test_empty_non_negative(self):
        assert abw_avg_words_per_paragraph(_EMPTY) >= 0.0

    def test_avg_le_max(self):
        assert abw_avg_words_per_paragraph(_TWO) <= abw_max_word_count_para(_TWO) + 1


# --- abw_digit_char_count ---

class TestAbwDigitCharCount:
    def test_returns_int(self):
        assert isinstance(abw_digit_char_count(_MINIMAL), int)

    def test_minimal_non_negative(self):
        assert abw_digit_char_count(_MINIMAL) >= 0

    def test_two_non_negative(self):
        assert abw_digit_char_count(_TWO) >= 0

    def test_empty_non_negative(self):
        assert abw_digit_char_count(_EMPTY) >= 0

    def test_non_negative(self):
        assert abw_digit_char_count(_MINIMAL) >= 0
