"""
ABW FOSS gap closure tests.

Closes:
  GAP-ABW-FOSS-ABW_PUNCTUAT-001  — abw_punctuation_count
  GAP-ABW-FOSS-ABW_MEDIAN_P-001  — abw_median_paragraph_length
  GAP-ABW-FOSS-ABW_DISTINCT-001  — abw_distinct_word_ratio
  GAP-ABW-FOSS-ABW_TOTAL_TE-001  — abw_total_text_length
  GAP-ABW-FOSS-ABW_NONEMPTY-001  — abw_nonempty_paragraph_ratio
  GAP-ABW-FOSS-ABW_HAS_NUME-001  — abw_has_numeric_content
  GAP-ABW-FOSS-ABW_NONSPACE-001  — abw_nonspace_char_count
  GAP-ABW-FOSS-ABW_LINE_COU-001  — abw_line_count
  GAP-ABW-FOSS-ABW_UPPERCAS-001  — abw_uppercase_ratio

Run from repo root:
    python -m pytest tests/python/abw/test_abw_gap_closure_foss.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

import pytest

from abw.abw_codec import (
    abw_punctuation_count,
    abw_median_paragraph_length,
    abw_distinct_word_ratio,
    abw_total_text_length,
    abw_nonempty_paragraph_ratio,
    abw_has_numeric_content,
    abw_nonspace_char_count,
    abw_line_count,
    abw_uppercase_ratio,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "abw"
MINIMAL = SAMPLES / "minimal-document.abw"
TWO_PARA = SAMPLES / "two-paragraphs.abw"
EMPTY = SAMPLES / "empty-section.abw"


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_PUNCTUAT-001 — abw_punctuation_count
# ---------------------------------------------------------------------------

class TestAbwPunctuationCount:
    def test_empty_document_returns_zero(self):
        assert abw_punctuation_count(EMPTY) == 0

    def test_minimal_document_no_punctuation(self):
        assert abw_punctuation_count(MINIMAL) == 0

    def test_two_paragraphs_has_punctuation(self):
        # two-paragraphs.abw contains 2 punctuation chars (period + comma)
        assert abw_punctuation_count(TWO_PARA) == 2

    def test_returns_int(self):
        assert isinstance(abw_punctuation_count(MINIMAL), int)

    def test_non_negative(self):
        assert abw_punctuation_count(EMPTY) >= 0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_MEDIAN_P-001 — abw_median_paragraph_length
# ---------------------------------------------------------------------------

class TestAbwMedianParagraphLength:
    def test_empty_document_returns_zero(self):
        assert abw_median_paragraph_length(EMPTY) == 0

    def test_minimal_document_length(self):
        # "Hello" = 5 chars
        assert abw_median_paragraph_length(MINIMAL) == 5

    def test_two_paragraphs_median(self):
        # Median of two paragraph lengths (16 chars)
        assert abw_median_paragraph_length(TWO_PARA) == 16

    def test_returns_numeric(self):
        result = abw_median_paragraph_length(MINIMAL)
        assert isinstance(result, (int, float))

    def test_non_negative(self):
        assert abw_median_paragraph_length(EMPTY) >= 0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_DISTINCT-001 — abw_distinct_word_ratio
# ---------------------------------------------------------------------------

class TestAbwDistinctWordRatio:
    def test_empty_document_returns_zero(self):
        assert abw_distinct_word_ratio(EMPTY) == 0.0

    def test_minimal_all_unique_words(self):
        # Single word "Hello" — distinct ratio = 1.0
        assert abw_distinct_word_ratio(MINIMAL) == pytest.approx(1.0, abs=0.01)

    def test_two_paragraphs_ratio(self):
        # Some repeated words — ratio < 1.0 or 0.75
        ratio = abw_distinct_word_ratio(TWO_PARA)
        assert 0.0 <= ratio <= 1.0

    def test_returns_float(self):
        result = abw_distinct_word_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_bounded_zero_to_one(self):
        for sample in [EMPTY, MINIMAL, TWO_PARA]:
            r = abw_distinct_word_ratio(sample)
            assert 0.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_TOTAL_TE-001 — abw_total_text_length
# ---------------------------------------------------------------------------

class TestAbwTotalTextLength:
    def test_empty_document_returns_zero(self):
        assert abw_total_text_length(EMPTY) == 0

    def test_minimal_document_length(self):
        assert abw_total_text_length(MINIMAL) == 5  # "Hello"

    def test_two_paragraphs_length(self):
        assert abw_total_text_length(TWO_PARA) == 33

    def test_returns_int(self):
        assert isinstance(abw_total_text_length(MINIMAL), int)

    def test_non_negative(self):
        assert abw_total_text_length(EMPTY) >= 0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_NONEMPTY-001 — abw_nonempty_paragraph_ratio
# ---------------------------------------------------------------------------

class TestAbwNonemptyParagraphRatio:
    def test_empty_document_returns_zero(self):
        assert abw_nonempty_paragraph_ratio(EMPTY) == 0.0

    def test_minimal_all_nonempty(self):
        assert abw_nonempty_paragraph_ratio(MINIMAL) == pytest.approx(1.0, abs=0.01)

    def test_two_paragraphs_all_nonempty(self):
        assert abw_nonempty_paragraph_ratio(TWO_PARA) == pytest.approx(1.0, abs=0.01)

    def test_returns_float(self):
        result = abw_nonempty_paragraph_ratio(MINIMAL)
        assert isinstance(result, float)

    def test_bounded_zero_to_one(self):
        for sample in [EMPTY, MINIMAL, TWO_PARA]:
            r = abw_nonempty_paragraph_ratio(sample)
            assert 0.0 <= r <= 1.0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_HAS_NUME-001 — abw_has_numeric_content
# ---------------------------------------------------------------------------

class TestAbwHasNumericContent:
    def test_empty_document_returns_false(self):
        assert abw_has_numeric_content(EMPTY) is False

    def test_minimal_no_numeric(self):
        assert abw_has_numeric_content(MINIMAL) is False

    def test_two_paragraphs_no_numeric(self):
        assert abw_has_numeric_content(TWO_PARA) is False

    def test_returns_bool(self):
        assert isinstance(abw_has_numeric_content(MINIMAL), bool)


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_NONSPACE-001 — abw_nonspace_char_count
# ---------------------------------------------------------------------------

class TestAbwNonspaceCharCount:
    def test_empty_document_returns_zero(self):
        assert abw_nonspace_char_count(EMPTY) == 0

    def test_minimal_document_count(self):
        assert abw_nonspace_char_count(MINIMAL) == 5  # "Hello" = 5 nonspace

    def test_two_paragraphs_count(self):
        assert abw_nonspace_char_count(TWO_PARA) == 31

    def test_returns_int(self):
        assert isinstance(abw_nonspace_char_count(MINIMAL), int)

    def test_non_negative(self):
        assert abw_nonspace_char_count(EMPTY) >= 0

    def test_less_than_or_equal_total_length(self):
        assert abw_nonspace_char_count(TWO_PARA) <= abw_total_text_length(TWO_PARA)


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_LINE_COU-001 — abw_line_count
# ---------------------------------------------------------------------------

class TestAbwLineCount:
    def test_empty_document_returns_zero(self):
        assert abw_line_count(EMPTY) == 0

    def test_minimal_one_line(self):
        assert abw_line_count(MINIMAL) == 1

    def test_two_paragraphs_two_lines(self):
        assert abw_line_count(TWO_PARA) == 2

    def test_returns_int(self):
        assert isinstance(abw_line_count(MINIMAL), int)

    def test_non_negative(self):
        assert abw_line_count(EMPTY) >= 0


# ---------------------------------------------------------------------------
# GAP-ABW-FOSS-ABW_UPPERCAS-001 — abw_uppercase_ratio
# ---------------------------------------------------------------------------

class TestAbwUppercaseRatio:
    def test_empty_document_returns_zero(self):
        assert abw_uppercase_ratio(EMPTY) == 0.0

    def test_minimal_has_uppercase(self):
        # "Hello" — 'H' is uppercase, ratio = 1/5 = 0.2
        assert abw_uppercase_ratio(MINIMAL) == pytest.approx(0.2, abs=0.01)

    def test_two_paragraphs_low_ratio(self):
        ratio = abw_uppercase_ratio(TWO_PARA)
        assert 0.0 <= ratio <= 1.0

    def test_returns_float(self):
        assert isinstance(abw_uppercase_ratio(MINIMAL), float)

    def test_bounded_zero_to_one(self):
        for sample in [EMPTY, MINIMAL, TWO_PARA]:
            r = abw_uppercase_ratio(sample)
            assert 0.0 <= r <= 1.0
