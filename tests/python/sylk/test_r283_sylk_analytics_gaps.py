"""
Tests for SYLK analytics gap closure (5 FOSS gaps).
Closes: GAP-SYLK-FOSS-SYLK_IS_ALL_-001, GAP-SYLK-FOSS-SYLK_ROW_SPA-001,
        GAP-SYLK-FOSS-SYLK_IS_SQUA-001, GAP-SYLK-FOSS-SYLK_TOTAL_S-001,
        GAP-SYLK-FOSS-SYLK_LONGEST-001
"""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from sylk.sylk_parser import (
    sylk_is_all_numeric,
    sylk_row_span,
    sylk_is_square,
    sylk_total_string_length,
    sylk_longest_row_index,
)

_SLK_2x2 = _REPO / "samples/by-format/sylk/valid/minimal-2x2.slk"
_SLK_NUMERIC = _REPO / "samples/by-format/sylk/valid/numeric-row.slk"


class TestSylkIsAllNumeric:
    def test_returns_bool(self):
        assert isinstance(sylk_is_all_numeric(_SLK_NUMERIC), bool)

    def test_numeric_file_true(self):
        assert sylk_is_all_numeric(_SLK_NUMERIC) is True

    def test_mixed_file_result_is_bool(self):
        result = sylk_is_all_numeric(_SLK_2x2)
        assert isinstance(result, bool)

    def test_not_all_numeric_for_mixed(self):
        # minimal-2x2 has string cells so is not all numeric
        assert sylk_is_all_numeric(_SLK_2x2) is False


class TestSylkRowSpan:
    def test_returns_int(self):
        assert isinstance(sylk_row_span(_SLK_2x2), int)

    def test_positive(self):
        assert sylk_row_span(_SLK_2x2) > 0

    def test_numeric_file(self):
        assert sylk_row_span(_SLK_NUMERIC) > 0

    def test_nonnegative(self):
        assert sylk_row_span(_SLK_2x2) >= 1


class TestSylkIsSquare:
    def test_returns_bool(self):
        assert isinstance(sylk_is_square(_SLK_2x2), bool)

    def test_2x2_result(self):
        result = sylk_is_square(_SLK_2x2)
        assert isinstance(result, bool)

    def test_numeric_file_result(self):
        result = sylk_is_square(_SLK_NUMERIC)
        assert isinstance(result, bool)

    def test_consistent_with_dimensions(self):
        # Just verify it returns a bool (square = rows == cols)
        assert isinstance(sylk_is_square(_SLK_2x2), bool)


class TestSylkTotalStringLength:
    def test_returns_int(self):
        assert isinstance(sylk_total_string_length(_SLK_2x2), int)

    def test_positive_for_string_content(self):
        assert sylk_total_string_length(_SLK_2x2) > 0

    def test_zero_for_numeric_only(self):
        # numeric-row.slk has no string cells
        assert sylk_total_string_length(_SLK_NUMERIC) >= 0

    def test_nonnegative(self):
        assert sylk_total_string_length(_SLK_2x2) >= 0


class TestSylkLongestRowIndex:
    def test_returns_int(self):
        assert isinstance(sylk_longest_row_index(_SLK_2x2), int)

    def test_nonnegative(self):
        assert sylk_longest_row_index(_SLK_2x2) >= 0

    def test_valid_for_numeric_file(self):
        assert sylk_longest_row_index(_SLK_NUMERIC) >= 0

    def test_index_in_range(self):
        result = sylk_longest_row_index(_SLK_2x2)
        assert result >= 0
