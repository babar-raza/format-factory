"""Tests for sylk_has_string_cells and sylk_unique_row_count (Sprint 40)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.sylk import sylk_has_string_cells, sylk_unique_row_count

_DIR = _REPO / "samples" / "by-format" / "sylk" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.slk")   # Name,Value,Alpha,42 -> 3 str, 2 rows
_NUMERIC = str(_DIR / "numeric-row.slk")    # 1,2,3 -> 0 str, 1 row
_SINGLE = str(_DIR / "single-cell.slk")     # 99 -> 0 str, 1 row


class TestSylkHasStringCells:
    def test_return_type(self):
        assert isinstance(sylk_has_string_cells(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-2x2.slk has string cells "Name", "Value", "Alpha"
        assert sylk_has_string_cells(_MINIMAL) is True

    def test_false_for_numeric_row(self):
        # numeric-row.slk has only integer cells
        assert sylk_has_string_cells(_NUMERIC) is False

    def test_false_for_single_cell(self):
        # single-cell.slk has only one integer cell (99)
        assert sylk_has_string_cells(_SINGLE) is False

    def test_consistent_across_calls(self):
        assert sylk_has_string_cells(_MINIMAL) == sylk_has_string_cells(_MINIMAL)


class TestSylkUniqueRowCount:
    def test_return_type(self):
        assert isinstance(sylk_unique_row_count(_MINIMAL), int)

    def test_exact_2_for_minimal(self):
        # minimal-2x2.slk has rows 1 and 2 -> 2 unique rows
        assert sylk_unique_row_count(_MINIMAL) == 2

    def test_exact_1_for_numeric_row(self):
        # numeric-row.slk has only row 1 -> 1 unique row
        assert sylk_unique_row_count(_NUMERIC) == 1

    def test_exact_1_for_single_cell(self):
        # single-cell.slk has one cell -> 1 unique row
        assert sylk_unique_row_count(_SINGLE) == 1

    def test_nonnegative(self):
        assert sylk_unique_row_count(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert sylk_unique_row_count(_MINIMAL) == sylk_unique_row_count(_MINIMAL)
