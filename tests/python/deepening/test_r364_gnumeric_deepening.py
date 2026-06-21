"""Sprint 134 — Gnumeric product deepening: row_col_ratio + numeric_to_string_ratio."""
import pytest
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

_EMPTY = str(_REPO / "samples" / "by-format" / "gnumeric" / "empty-sheet.gnumeric")
_MINIMAL = str(_REPO / "samples" / "by-format" / "gnumeric" / "minimal-spreadsheet.gnumeric")
_MULTI = str(_REPO / "samples" / "by-format" / "gnumeric" / "multi-cell-basic.gnumeric")


class TestGnumericRowColRatio:
    def test_return_type(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert isinstance(gnumeric_row_col_ratio(_MINIMAL), (int, float))

    def test_exact_0_for_empty(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert gnumeric_row_col_ratio(_EMPTY) == pytest.approx(0.0)

    def test_exact_1_for_minimal(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert gnumeric_row_col_ratio(_MINIMAL) == pytest.approx(1.0)

    def test_exact_1_for_multi(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert gnumeric_row_col_ratio(_MULTI) == pytest.approx(1.0)

    def test_nonnegative(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert gnumeric_row_col_ratio(_MINIMAL) >= 0.0

    def test_consistent(self):
        from src.python.gnumeric import gnumeric_row_col_ratio
        assert gnumeric_row_col_ratio(_MINIMAL) == gnumeric_row_col_ratio(_MINIMAL)


class TestGnumericNumericToStringRatio:
    def test_return_type(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        assert isinstance(gnumeric_numeric_to_string_ratio(_MINIMAL), (int, float))

    def test_exact_0_for_empty(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        assert gnumeric_numeric_to_string_ratio(_EMPTY) == pytest.approx(0.0)

    def test_exact_0_for_minimal(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        # minimal-spreadsheet has only string cells
        assert gnumeric_numeric_to_string_ratio(_MINIMAL) == pytest.approx(0.0)

    def test_exact_0_for_multi(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        # multi-cell-basic has only string cells
        assert gnumeric_numeric_to_string_ratio(_MULTI) == pytest.approx(0.0)

    def test_nonnegative(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        assert gnumeric_numeric_to_string_ratio(_MINIMAL) >= 0.0

    def test_consistent(self):
        from src.python.gnumeric import gnumeric_numeric_to_string_ratio
        assert gnumeric_numeric_to_string_ratio(_MINIMAL) == gnumeric_numeric_to_string_ratio(_MINIMAL)
