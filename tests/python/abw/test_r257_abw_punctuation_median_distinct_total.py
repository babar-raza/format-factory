"""Tests for ABW gap closure (Sprint 40).

Closes:
  GAP-ABW-FOSS-ABW_PUNCTUAT-001   (Abw Punctuation Count)
  GAP-ABW-FOSS-ABW_MEDIAN_P-001   (Abw Median Paragraph Length)
  GAP-ABW-FOSS-ABW_DISTINCT-001   (Abw Distinct Word Ratio)
  GAP-ABW-FOSS-ABW_TOTAL_TE-001   (Abw Total Text Length)
  GAP-ABW-FOSS-ABW_NONEMPTY-001   (Abw Nonempty Paragraph Ratio)
  GAP-ABW-FOSS-ABW_HAS_NUME-001   (Abw Has Numeric Content)
  GAP-ABW-FOSS-ABW_NONSPACE-001   (Abw Nonspace Char Count)
  GAP-ABW-FOSS-ABW_LINE_COU-001   (Abw Line Count)
  GAP-ABW-FOSS-ABW_UPPERCAS-001   (Abw Uppercase Ratio)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.abw import (
    abw_distinct_word_ratio,
    abw_has_numeric_content,
    abw_line_count,
    abw_median_paragraph_length,
    abw_nonempty_paragraph_ratio,
    abw_nonspace_char_count,
    abw_punctuation_count,
    abw_total_text_length,
    abw_uppercase_ratio,
)

_DIR = _REPO / "samples" / "by-format" / "abw"
_EMPTY = str(_DIR / "empty-section.abw")
_MINIMAL = str(_DIR / "minimal-document.abw")
_TWO_PARAS = str(_DIR / "two-paragraphs.abw")


class TestAbwPunctuationCount:
    def test_return_type(self):
        assert isinstance(abw_punctuation_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert abw_punctuation_count(_EMPTY) == 0

    def test_zero_for_minimal(self):
        assert abw_punctuation_count(_MINIMAL) == 0

    def test_exact_2_for_two_paragraphs(self):
        assert abw_punctuation_count(_TWO_PARAS) == 2

    def test_nonnegative(self):
        assert abw_punctuation_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_punctuation_count(_TWO_PARAS) == abw_punctuation_count(_TWO_PARAS)


class TestAbwMedianParagraphLength:
    def test_return_type(self):
        assert isinstance(abw_median_paragraph_length(_MINIMAL), (int, float))

    def test_zero_for_empty(self):
        assert abw_median_paragraph_length(_EMPTY) == 0

    def test_exact_5_for_minimal(self):
        assert abw_median_paragraph_length(_MINIMAL) == 5

    def test_exact_16_for_two_paragraphs(self):
        assert abw_median_paragraph_length(_TWO_PARAS) == 16

    def test_nonnegative(self):
        assert abw_median_paragraph_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_median_paragraph_length(_MINIMAL) == abw_median_paragraph_length(_MINIMAL)


class TestAbwDistinctWordRatio:
    def test_return_type(self):
        assert isinstance(abw_distinct_word_ratio(_MINIMAL), float)

    def test_zero_for_empty(self):
        assert abw_distinct_word_ratio(_EMPTY) == 0.0

    def test_exact_1_0_for_minimal(self):
        # "Hello" -> 1 unique word out of 1 word = 1.0
        assert abw_distinct_word_ratio(_MINIMAL) == 1.0

    def test_exact_0_75_for_two_paragraphs(self):
        assert abw_distinct_word_ratio(_TWO_PARAS) == 0.75

    def test_between_0_and_1(self):
        ratio = abw_distinct_word_ratio(_MINIMAL)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert abw_distinct_word_ratio(_TWO_PARAS) == abw_distinct_word_ratio(_TWO_PARAS)


class TestAbwTotalTextLength:
    def test_return_type(self):
        assert isinstance(abw_total_text_length(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert abw_total_text_length(_EMPTY) == 0

    def test_exact_5_for_minimal(self):
        assert abw_total_text_length(_MINIMAL) == 5

    def test_exact_33_for_two_paragraphs(self):
        assert abw_total_text_length(_TWO_PARAS) == 33

    def test_nonnegative(self):
        assert abw_total_text_length(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_total_text_length(_TWO_PARAS) == abw_total_text_length(_TWO_PARAS)


class TestAbwNonemptyParagraphRatio:
    def test_return_type(self):
        assert isinstance(abw_nonempty_paragraph_ratio(_MINIMAL), float)

    def test_zero_for_empty(self):
        assert abw_nonempty_paragraph_ratio(_EMPTY) == 0.0

    def test_exact_1_0_for_minimal(self):
        assert abw_nonempty_paragraph_ratio(_MINIMAL) == 1.0

    def test_exact_1_0_for_two_paragraphs(self):
        assert abw_nonempty_paragraph_ratio(_TWO_PARAS) == 1.0

    def test_between_0_and_1(self):
        ratio = abw_nonempty_paragraph_ratio(_MINIMAL)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert abw_nonempty_paragraph_ratio(_MINIMAL) == abw_nonempty_paragraph_ratio(_MINIMAL)


class TestAbwHasNumericContent:
    def test_return_type(self):
        assert isinstance(abw_has_numeric_content(_MINIMAL), bool)

    def test_false_for_empty(self):
        assert abw_has_numeric_content(_EMPTY) is False

    def test_false_for_minimal(self):
        assert abw_has_numeric_content(_MINIMAL) is False

    def test_false_for_two_paragraphs(self):
        assert abw_has_numeric_content(_TWO_PARAS) is False

    def test_consistent_across_calls(self):
        assert abw_has_numeric_content(_MINIMAL) == abw_has_numeric_content(_MINIMAL)


class TestAbwNonspaceCharCount:
    def test_return_type(self):
        assert isinstance(abw_nonspace_char_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert abw_nonspace_char_count(_EMPTY) == 0

    def test_exact_5_for_minimal(self):
        assert abw_nonspace_char_count(_MINIMAL) == 5

    def test_exact_31_for_two_paragraphs(self):
        assert abw_nonspace_char_count(_TWO_PARAS) == 31

    def test_nonnegative(self):
        assert abw_nonspace_char_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_nonspace_char_count(_TWO_PARAS) == abw_nonspace_char_count(_TWO_PARAS)


class TestAbwLineCount:
    def test_return_type(self):
        assert isinstance(abw_line_count(_MINIMAL), int)

    def test_zero_for_empty(self):
        assert abw_line_count(_EMPTY) == 0

    def test_exact_1_for_minimal(self):
        assert abw_line_count(_MINIMAL) == 1

    def test_exact_2_for_two_paragraphs(self):
        assert abw_line_count(_TWO_PARAS) == 2

    def test_nonnegative(self):
        assert abw_line_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert abw_line_count(_TWO_PARAS) == abw_line_count(_TWO_PARAS)


class TestAbwUppercaseRatio:
    def test_return_type(self):
        assert isinstance(abw_uppercase_ratio(_MINIMAL), float)

    def test_zero_for_empty(self):
        assert abw_uppercase_ratio(_EMPTY) == 0.0

    def test_exact_0_2_for_minimal(self):
        # "Hello": H is uppercase -> 1/5 = 0.2
        assert abw_uppercase_ratio(_MINIMAL) == 0.2

    def test_between_0_and_1(self):
        ratio = abw_uppercase_ratio(_MINIMAL)
        assert 0.0 <= ratio <= 1.0

    def test_consistent_across_calls(self):
        assert abw_uppercase_ratio(_MINIMAL) == abw_uppercase_ratio(_MINIMAL)
