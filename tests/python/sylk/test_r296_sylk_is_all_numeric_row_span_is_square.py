"""Tests for SYLK gap closure (Sprint 40).

Closes:
  GAP-SYLK-FOSS-SYLK_IS_ALL_-001  (Sylk Is All Numeric)
  GAP-SYLK-FOSS-SYLK_ROW_SPA-001  (Sylk Row Span)
  GAP-SYLK-FOSS-SYLK_IS_SQUA-001  (Sylk Is Square)
  GAP-SYLK-FOSS-SYLK_TOTAL_S-001  (Sylk Total String Length)
  GAP-SYLK-FOSS-SYLK_LONGEST-001  (Sylk Longest Row Index)
  GAP-SYLK-FOSS-SYLK_STRING_-001  (Sylk String Value Count)
"""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import (
    sylk_is_all_numeric,
    sylk_is_square,
    sylk_longest_row_index,
    sylk_row_span,
    sylk_string_value_count,
    sylk_total_string_length,
)

_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL_2X2 = str(_DIR / "minimal-2x2.slk")
_NUMERIC_ROW = str(_DIR / "numeric-row.slk")
_SINGLE_CELL = str(_DIR / "single-cell.slk")


class TestSylkIsAllNumeric:
    def test_return_type(self):
        assert isinstance(sylk_is_all_numeric(_MINIMAL_2X2), bool)

    def test_false_for_minimal_2x2(self):
        # minimal-2x2 has string header cells -> not all numeric
        assert sylk_is_all_numeric(_MINIMAL_2X2) is False

    def test_true_for_numeric_row(self):
        assert sylk_is_all_numeric(_NUMERIC_ROW) is True

    def test_true_for_single_cell(self):
        assert sylk_is_all_numeric(_SINGLE_CELL) is True

    def test_consistent_across_calls(self):
        assert sylk_is_all_numeric(_MINIMAL_2X2) == sylk_is_all_numeric(_MINIMAL_2X2)


class TestSylkRowSpan:
    def test_return_type(self):
        assert isinstance(sylk_row_span(_MINIMAL_2X2), int)

    def test_exact_2_for_minimal_2x2(self):
        assert sylk_row_span(_MINIMAL_2X2) == 2

    def test_exact_1_for_numeric_row(self):
        assert sylk_row_span(_NUMERIC_ROW) == 1

    def test_exact_1_for_single_cell(self):
        assert sylk_row_span(_SINGLE_CELL) == 1

    def test_nonnegative(self):
        assert sylk_row_span(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert sylk_row_span(_MINIMAL_2X2) == sylk_row_span(_MINIMAL_2X2)


class TestSylkIsSquare:
    def test_return_type(self):
        assert isinstance(sylk_is_square(_MINIMAL_2X2), bool)

    def test_true_for_minimal_2x2(self):
        # 2x2 is square
        assert sylk_is_square(_MINIMAL_2X2) is True

    def test_false_for_numeric_row(self):
        # 1 row, multiple columns -> not square
        assert sylk_is_square(_NUMERIC_ROW) is False

    def test_true_for_single_cell(self):
        # 1x1 is square
        assert sylk_is_square(_SINGLE_CELL) is True

    def test_consistent_across_calls(self):
        assert sylk_is_square(_MINIMAL_2X2) == sylk_is_square(_MINIMAL_2X2)


class TestSylkTotalStringLength:
    def test_return_type(self):
        assert isinstance(sylk_total_string_length(_MINIMAL_2X2), int)

    def test_exact_16_for_minimal_2x2(self):
        assert sylk_total_string_length(_MINIMAL_2X2) == 16

    def test_exact_3_for_numeric_row(self):
        assert sylk_total_string_length(_NUMERIC_ROW) == 3

    def test_exact_2_for_single_cell(self):
        assert sylk_total_string_length(_SINGLE_CELL) == 2

    def test_nonnegative(self):
        assert sylk_total_string_length(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert sylk_total_string_length(_MINIMAL_2X2) == sylk_total_string_length(_MINIMAL_2X2)


class TestSylkLongestRowIndex:
    def test_return_type(self):
        assert isinstance(sylk_longest_row_index(_MINIMAL_2X2), int)

    def test_exact_1_for_minimal_2x2(self):
        assert sylk_longest_row_index(_MINIMAL_2X2) == 1

    def test_exact_1_for_numeric_row(self):
        assert sylk_longest_row_index(_NUMERIC_ROW) == 1

    def test_exact_1_for_single_cell(self):
        assert sylk_longest_row_index(_SINGLE_CELL) == 1

    def test_consistent_across_calls(self):
        assert sylk_longest_row_index(_MINIMAL_2X2) == sylk_longest_row_index(_MINIMAL_2X2)


class TestSylkStringValueCount:
    def test_return_type(self):
        assert isinstance(sylk_string_value_count(_MINIMAL_2X2), int)

    def test_exact_3_for_minimal_2x2(self):
        assert sylk_string_value_count(_MINIMAL_2X2) == 3

    def test_exact_0_for_numeric_row(self):
        assert sylk_string_value_count(_NUMERIC_ROW) == 0

    def test_exact_0_for_single_cell(self):
        assert sylk_string_value_count(_SINGLE_CELL) == 0

    def test_nonnegative(self):
        assert sylk_string_value_count(_MINIMAL_2X2) >= 0

    def test_consistent_across_calls(self):
        assert sylk_string_value_count(_MINIMAL_2X2) == sylk_string_value_count(_MINIMAL_2X2)
