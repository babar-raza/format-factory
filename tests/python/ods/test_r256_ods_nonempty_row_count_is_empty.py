"""Tests for ods_nonempty_row_count and ods_is_empty (Sprint 46)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_nonempty_row_count, ods_is_empty

_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_DIR / "minimal-spreadsheet.ods")  # 2 rows, 2 cols, 4 cells
_NUMERIC = str(_DIR / "numeric-row.ods")           # 1 row, 3 cols, 3 numeric cells
_SINGLE = str(_DIR / "single-cell.ods")            # 1 row, 1 col, 1 string cell


class TestOdsNonemptyRowCount:
    def test_return_type(self):
        assert isinstance(ods_nonempty_row_count(_MINIMAL), int)

    def test_minimal_exact_2(self):
        # minimal-spreadsheet.ods has 2 rows, both non-empty
        assert ods_nonempty_row_count(_MINIMAL) == 2

    def test_numeric_row_exact_1(self):
        # numeric-row.ods has 1 row, non-empty
        assert ods_nonempty_row_count(_NUMERIC) == 1

    def test_single_cell_exact_1(self):
        # single-cell.ods has 1 row, non-empty
        assert ods_nonempty_row_count(_SINGLE) == 1

    def test_nonnegative(self):
        assert ods_nonempty_row_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert ods_nonempty_row_count(_MINIMAL) == ods_nonempty_row_count(_MINIMAL)

    def test_le_total_row_count(self):
        from src.python.ods import ods_row_count
        assert ods_nonempty_row_count(_MINIMAL) <= ods_row_count(_MINIMAL)


class TestOdsIsEmpty:
    def test_return_type(self):
        assert isinstance(ods_is_empty(_MINIMAL), bool)

    def test_false_for_minimal(self):
        # minimal-spreadsheet.ods has 4 cells — not empty
        assert ods_is_empty(_MINIMAL) is False

    def test_false_for_numeric_row(self):
        # numeric-row.ods has 3 numeric cells — not empty
        assert ods_is_empty(_NUMERIC) is False

    def test_false_for_single_cell(self):
        # single-cell.ods has 1 string cell — not empty
        assert ods_is_empty(_SINGLE) is False

    def test_consistent_across_calls(self):
        assert ods_is_empty(_MINIMAL) == ods_is_empty(_MINIMAL)

    def test_empty_implies_zero_nonempty_rows(self):
        # If not empty, nonempty_row_count > 0
        if not ods_is_empty(_MINIMAL):
            assert ods_nonempty_row_count(_MINIMAL) > 0
