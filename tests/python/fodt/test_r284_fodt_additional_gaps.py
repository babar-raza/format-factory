"""
Tests for additional FODT analytics gap closure (6 FOSS gaps).
Closes: FODT_TOTAL_T, FODT_HAS_NUM, FODT_AVG_SEN,
        FODT_MAX_HEA, FODT_TOTAL_C, FODT_IS_TEXT
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from fodt import (
    fodt_total_table_cells,
    fodt_has_numeric_content,
    fodt_avg_sentence_length,
    fodt_max_heading_depth,
    fodt_total_char_count,
    fodt_is_text_heavy,
)

_MINIMAL = _REPO / "samples/by-format/fodt/minimal-document.fodt"
_HEADINGS = _REPO / "samples/by-format/fodt/headings-and-paragraphs.fodt"


class TestFodtTotalTableCells:
    def test_returns_int(self):
        assert isinstance(fodt_total_table_cells(_MINIMAL), int)

    def test_nonnegative(self):
        assert fodt_total_table_cells(_MINIMAL) >= 0

    def test_minimal_no_tables(self):
        # minimal-document has no tables
        assert fodt_total_table_cells(_MINIMAL) == 0

    def test_headings_no_tables(self):
        assert fodt_total_table_cells(_HEADINGS) == 0


class TestFodtHasNumericContent:
    def test_returns_bool(self):
        assert isinstance(fodt_has_numeric_content(_MINIMAL), bool)

    def test_minimal_no_numeric(self):
        assert fodt_has_numeric_content(_MINIMAL) is False

    def test_headings_no_numeric(self):
        assert fodt_has_numeric_content(_HEADINGS) is False

    def test_consistent_type(self):
        result = fodt_has_numeric_content(_HEADINGS)
        assert result is True or result is False


class TestFodtAvgSentenceLength:
    def test_returns_float(self):
        assert isinstance(fodt_avg_sentence_length(_MINIMAL), float)

    def test_nonnegative(self):
        assert fodt_avg_sentence_length(_MINIMAL) >= 0.0

    def test_minimal_value(self):
        assert fodt_avg_sentence_length(_MINIMAL) == pytest.approx(12.0)

    def test_headings_longer(self):
        # headings-and-paragraphs has longer sentences
        assert fodt_avg_sentence_length(_HEADINGS) > fodt_avg_sentence_length(_MINIMAL)


class TestFodtMaxHeadingDepth:
    def test_returns_int(self):
        assert isinstance(fodt_max_heading_depth(_MINIMAL), int)

    def test_nonnegative(self):
        assert fodt_max_heading_depth(_MINIMAL) >= 0

    def test_minimal_no_headings(self):
        assert fodt_max_heading_depth(_MINIMAL) == 0

    def test_headings_doc_has_depth(self):
        assert fodt_max_heading_depth(_HEADINGS) == 1


class TestFodtTotalCharCount:
    def test_returns_int(self):
        assert isinstance(fodt_total_char_count(_MINIMAL), int)

    def test_nonnegative(self):
        assert fodt_total_char_count(_MINIMAL) >= 0

    def test_minimal_value(self):
        assert fodt_total_char_count(_MINIMAL) == 13

    def test_headings_larger(self):
        assert fodt_total_char_count(_HEADINGS) > fodt_total_char_count(_MINIMAL)


class TestFodtIsTextHeavy:
    def test_returns_bool(self):
        assert isinstance(fodt_is_text_heavy(_MINIMAL), bool)

    def test_minimal_not_text_heavy(self):
        # minimal-document is short → not text heavy
        assert fodt_is_text_heavy(_MINIMAL) is False

    def test_headings_is_text_heavy(self):
        assert fodt_is_text_heavy(_HEADINGS) is True

    def test_consistent_type(self):
        result = fodt_is_text_heavy(_HEADINGS)
        assert result is True or result is False
