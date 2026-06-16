"""Tests for dif_has_string_cells and dif_max_numeric_value (Sprint 39)."""
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.dif import dif_has_string_cells, dif_max_numeric_value

_DIR = _REPO / "samples" / "by-format" / "dif" / "valid"
_MINIMAL = str(_DIR / "minimal-2x2.dif")   # has strings "Name","Value","Alpha","Beta" + nums 42.0, 99.0
_NUMERIC = str(_DIR / "numeric-row.dif")    # only floats: 1.0, 2.0, 3.0
_SINGLE = str(_DIR / "single-cell.dif")     # single float 42.0


class TestDifHasStringCells:
    def test_return_type(self):
        assert isinstance(dif_has_string_cells(_MINIMAL), bool)

    def test_true_for_minimal(self):
        # minimal-2x2.dif has string cells "Name", "Alpha", etc.
        assert dif_has_string_cells(_MINIMAL) is True

    def test_false_for_numeric_row(self):
        # numeric-row.dif has only float cells
        assert dif_has_string_cells(_NUMERIC) is False

    def test_false_for_single_cell(self):
        # single-cell.dif has only one float cell
        assert dif_has_string_cells(_SINGLE) is False

    def test_consistent_across_calls(self):
        assert dif_has_string_cells(_MINIMAL) == dif_has_string_cells(_MINIMAL)


class TestDifMaxNumericValue:
    def test_return_type(self):
        result = dif_max_numeric_value(_MINIMAL)
        assert isinstance(result, float)

    def test_exact_99_for_minimal(self):
        # minimal-2x2.dif has numeric cells 42.0, 99.0 -> max=99.0
        assert dif_max_numeric_value(_MINIMAL) == 99.0

    def test_exact_3_for_numeric_row(self):
        # numeric-row.dif: 1.0, 2.0, 3.0 -> max=3.0
        assert dif_max_numeric_value(_NUMERIC) == 3.0

    def test_exact_42_for_single(self):
        # single-cell.dif: 42.0
        assert dif_max_numeric_value(_SINGLE) == 42.0

    def test_nonnegative_for_minimal(self):
        assert dif_max_numeric_value(_MINIMAL) >= 0

    def test_consistent_across_calls(self):
        assert dif_max_numeric_value(_MINIMAL) == dif_max_numeric_value(_MINIMAL)
