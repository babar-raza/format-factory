"""Tests for ods_max_numeric_value and ods_has_string_cells (Sprint 41)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ods import ods_max_numeric_value, ods_has_string_cells

_DIR = _REPO / "samples" / "by-format" / "ods" / "valid"
_MINIMAL = str(_DIR / "minimal-spreadsheet.ods")   # Name,Score,Alice,42.0 -> max=42.0, has_str=True
_NUMERIC = str(_DIR / "numeric-row.ods")            # 1.0,2.0,3.0 -> max=3.0, has_str=False
_SINGLE = str(_DIR / "single-cell.ods")             # "A1" -> max=None, has_str=True


class TestOdsMaxNumericValue:
    def test_return_type_for_numeric_file(self):
        result = ods_max_numeric_value(_MINIMAL)
        assert isinstance(result, (int, float))

    def test_exact_42_for_minimal(self):
        # minimal-spreadsheet.ods has numeric cell 42.0
        assert ods_max_numeric_value(_MINIMAL) == 42.0

    def test_exact_3_for_numeric_row(self):
        # numeric-row.ods has 1.0, 2.0, 3.0 -> max=3.0
        assert ods_max_numeric_value(_NUMERIC) == 3.0

    def test_none_for_string_only(self):
        # single-cell.ods has only string "A1" -> None
        assert ods_max_numeric_value(_SINGLE) is None

    def test_nonnegative_for_minimal(self):
        assert ods_max_numeric_value(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert ods_max_numeric_value(_MINIMAL) == ods_max_numeric_value(_MINIMAL)


class TestOdsHasStringCells:
    def test_return_type(self):
        assert isinstance(ods_has_string_cells(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-spreadsheet.ods has string cells "Name", "Alice"
        assert ods_has_string_cells(_MINIMAL) is True

    def test_false_for_numeric_row(self):
        # numeric-row.ods has only numeric cells
        assert ods_has_string_cells(_NUMERIC) is False

    def test_true_for_single_string(self):
        # single-cell.ods has "A1"
        assert ods_has_string_cells(_SINGLE) is True

    def test_consistent_across_calls(self):
        assert ods_has_string_cells(_MINIMAL) == ods_has_string_cells(_MINIMAL)
