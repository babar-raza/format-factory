"""
Tests for additional ABW analytics gap closure (7 FOSS gaps).
Closes: GAP-ABW-FOSS-DISTINCT_WORD_RATIO-001, GAP-ABW-FOSS-TOTAL_TEXT_LENGTH-001,
        GAP-ABW-FOSS-NONEMPTY_PARA_RATIO-001, GAP-ABW-FOSS-HAS_NUMERIC-001,
        GAP-ABW-FOSS-NONSPACE_CHAR-001, GAP-ABW-FOSS-LINE_COUNT-001,
        GAP-ABW-FOSS-UPPERCASE_RATIO-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from abw.abw_codec import (
    abw_distinct_word_ratio,
    abw_total_text_length,
    abw_nonempty_paragraph_ratio,
    abw_has_numeric_content,
    abw_nonspace_char_count,
    abw_line_count,
    abw_uppercase_ratio,
)

_MINIMAL = _REPO / "samples/by-format/abw/minimal-document.abw"
_TWO_PARA = _REPO / "samples/by-format/abw/two-paragraphs.abw"
_EMPTY = _REPO / "samples/by-format/abw/empty-section.abw"


class TestAbwDistinctWordRatio:
    def test_returns_float(self):
        assert isinstance(abw_distinct_word_ratio(_MINIMAL), float)

    def test_empty_returns_zero(self):
        assert abw_distinct_word_ratio(_EMPTY) == 0.0

    def test_minimal_all_unique_returns_one(self):
        # minimal-document has one short paragraph with all unique words → ratio 1.0
        assert abw_distinct_word_ratio(_MINIMAL) == pytest.approx(1.0)

    def test_two_paragraphs_less_than_one(self):
        # two-paragraphs has repeated words → ratio < 1.0
        result = abw_distinct_word_ratio(_TWO_PARA)
        assert 0.0 < result < 1.0


class TestAbwTotalTextLength:
    def test_returns_int(self):
        assert isinstance(abw_total_text_length(_MINIMAL), int)

    def test_empty_returns_zero(self):
        assert abw_total_text_length(_EMPTY) == 0

    def test_minimal_exact_value(self):
        # minimal-document paragraph text is 5 characters
        assert abw_total_text_length(_MINIMAL) == 5

    def test_two_paragraphs_greater_than_minimal(self):
        assert abw_total_text_length(_TWO_PARA) > abw_total_text_length(_MINIMAL)


class TestAbwNonemptyParagraphRatio:
    def test_returns_float(self):
        assert isinstance(abw_nonempty_paragraph_ratio(_MINIMAL), float)

    def test_empty_section_returns_zero(self):
        assert abw_nonempty_paragraph_ratio(_EMPTY) == 0.0

    def test_minimal_all_nonempty(self):
        assert abw_nonempty_paragraph_ratio(_MINIMAL) == pytest.approx(1.0)

    def test_two_paragraphs_all_nonempty(self):
        assert abw_nonempty_paragraph_ratio(_TWO_PARA) == pytest.approx(1.0)


class TestAbwHasNumericContent:
    def test_returns_bool(self):
        assert isinstance(abw_has_numeric_content(_MINIMAL), bool)

    def test_empty_returns_false(self):
        assert abw_has_numeric_content(_EMPTY) is False

    def test_minimal_no_digits(self):
        assert abw_has_numeric_content(_MINIMAL) is False

    def test_two_paragraphs_no_digits(self):
        assert abw_has_numeric_content(_TWO_PARA) is False


class TestAbwNonspaceCharCount:
    def test_returns_int(self):
        assert isinstance(abw_nonspace_char_count(_MINIMAL), int)

    def test_empty_returns_zero(self):
        assert abw_nonspace_char_count(_EMPTY) == 0

    def test_minimal_exact_value(self):
        # minimal-document: 5 chars, no spaces → nonspace = 5
        assert abw_nonspace_char_count(_MINIMAL) == 5

    def test_two_paragraphs_less_than_total_length(self):
        # nonspace count ≤ total text length (spaces excluded)
        assert abw_nonspace_char_count(_TWO_PARA) <= abw_total_text_length(_TWO_PARA)


class TestAbwLineCount:
    def test_returns_int(self):
        assert isinstance(abw_line_count(_MINIMAL), int)

    def test_empty_returns_zero(self):
        assert abw_line_count(_EMPTY) == 0

    def test_minimal_one_paragraph_one_line(self):
        assert abw_line_count(_MINIMAL) == 1

    def test_two_paragraphs_two_lines(self):
        assert abw_line_count(_TWO_PARA) == 2


class TestAbwUppercaseRatio:
    def test_returns_float(self):
        assert isinstance(abw_uppercase_ratio(_MINIMAL), float)

    def test_empty_returns_zero(self):
        assert abw_uppercase_ratio(_EMPTY) == 0.0

    def test_minimal_has_uppercase(self):
        # minimal-document starts with capital → ratio > 0
        assert abw_uppercase_ratio(_MINIMAL) > 0.0

    def test_ratio_bounded(self):
        result = abw_uppercase_ratio(_TWO_PARA)
        assert 0.0 <= result <= 1.0
