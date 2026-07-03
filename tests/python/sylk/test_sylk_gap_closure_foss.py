"""
SYLK FOSS gap closure tests.

Closes:
  GAP-SYLK-FOSS-SYLK_ROW_SPA-001  — sylk_row_span
  GAP-SYLK-FOSS-SYLK_IS_SQUA-001  — sylk_is_square
  GAP-SYLK-FOSS-SYLK_TOTAL_S-001  — sylk_total_string_length
  GAP-SYLK-FOSS-SYLK_LONGEST-001  — sylk_longest_row_index
  GAP-SYLK-FOSS-SYLK_STRING_-001  — sylk_string_value_count

Run from repo root:
    python -m pytest tests/python/sylk/test_sylk_gap_closure_foss.py -v
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "src" / "python"))

from sylk.sylk_analytics import (
    sylk_row_span,
    sylk_is_square,
    sylk_total_string_length,
    sylk_longest_row_index,
    sylk_string_value_count,
)

SAMPLES = REPO_ROOT / "samples" / "by-format" / "sylk" / "valid"
SINGLE = SAMPLES / "single-cell.slk"
TWO_X_TWO = SAMPLES / "minimal-2x2.slk"
NUMERIC = SAMPLES / "numeric-row.slk"


# ---------------------------------------------------------------------------
# GAP-SYLK-FOSS-SYLK_ROW_SPA-001 — sylk_row_span
# ---------------------------------------------------------------------------

class TestSylkRowSpan:
    def test_single_cell_row_span_one(self):
        assert sylk_row_span(SINGLE) == 1

    def test_two_x_two_row_span_two(self):
        assert sylk_row_span(TWO_X_TWO) == 2

    def test_returns_int(self):
        assert isinstance(sylk_row_span(SINGLE), int)

    def test_positive(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert sylk_row_span(p) > 0


# ---------------------------------------------------------------------------
# GAP-SYLK-FOSS-SYLK_IS_SQUA-001 — sylk_is_square
# ---------------------------------------------------------------------------

class TestSylkIsSquare:
    def test_single_cell_is_square(self):
        assert sylk_is_square(SINGLE) is True

    def test_two_x_two_is_square(self):
        assert sylk_is_square(TWO_X_TWO) is True

    def test_numeric_row_not_square(self):
        # numeric-row.slk has row_span=1, col_span!=1
        assert sylk_is_square(NUMERIC) is False

    def test_returns_bool(self):
        assert isinstance(sylk_is_square(SINGLE), bool)


# ---------------------------------------------------------------------------
# GAP-SYLK-FOSS-SYLK_TOTAL_S-001 — sylk_total_string_length
# ---------------------------------------------------------------------------

class TestSylkTotalStringLength:
    def test_single_cell_positive(self):
        assert sylk_total_string_length(SINGLE) > 0

    def test_two_x_two_larger_than_single(self):
        assert sylk_total_string_length(TWO_X_TWO) > sylk_total_string_length(SINGLE)

    def test_returns_int(self):
        assert isinstance(sylk_total_string_length(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert sylk_total_string_length(p) >= 0


# ---------------------------------------------------------------------------
# GAP-SYLK-FOSS-SYLK_LONGEST-001 — sylk_longest_row_index
# ---------------------------------------------------------------------------

class TestSylkLongestRowIndex:
    def test_single_cell_index_one(self):
        assert sylk_longest_row_index(SINGLE) == 1

    def test_two_x_two_index_one(self):
        assert sylk_longest_row_index(TWO_X_TWO) == 1

    def test_returns_int(self):
        assert isinstance(sylk_longest_row_index(SINGLE), int)


# ---------------------------------------------------------------------------
# GAP-SYLK-FOSS-SYLK_STRING_-001 — sylk_string_value_count
# ---------------------------------------------------------------------------

class TestSylkStringValueCount:
    def test_single_cell_zero(self):
        assert sylk_string_value_count(SINGLE) == 0

    def test_two_x_two_has_strings(self):
        assert sylk_string_value_count(TWO_X_TWO) > 0

    def test_returns_int(self):
        assert isinstance(sylk_string_value_count(SINGLE), int)

    def test_non_negative(self):
        for p in [SINGLE, TWO_X_TWO, NUMERIC]:
            assert sylk_string_value_count(p) >= 0
