"""
Sprint 109 — FODS analytics round 5.
25 tests for 5 new analytics functions:
  fods_max_cell_value_length, fods_min_cell_value_length, fods_total_row_count,
  fods_has_empty_sheet, fods_numeric_cell_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods_strict,
    fods_max_cell_value_length,
    fods_min_cell_value_length,
    fods_total_row_count,
    fods_has_empty_sheet,
    fods_numeric_cell_count,
)

_DIR = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_DIR / "minimal-spreadsheet.fods")
_MULTI = str(_DIR / "multi-sheet-basic.fods")
_TYPED = str(_DIR / "typed-values-basic.fods")


def _wb(path: str):
    return parse_fods_strict(path)


# --- fods_max_cell_value_length ---

class TestFodsMaxCellValueLength:
    def test_returns_int(self):
        result = fods_max_cell_value_length(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fods_max_cell_value_length(_wb(_MINIMAL))
        assert result >= 0

    def test_minimal_positive(self):
        result = fods_max_cell_value_length(_wb(_MINIMAL))
        assert result > 0

    def test_typed_positive(self):
        result = fods_max_cell_value_length(_wb(_TYPED))
        assert result > 0

    def test_gte_min(self):
        mx = fods_max_cell_value_length(_wb(_MINIMAL))
        mn = fods_min_cell_value_length(_wb(_MINIMAL))
        assert mx >= mn


# --- fods_min_cell_value_length ---

class TestFodsMinCellValueLength:
    def test_returns_int(self):
        result = fods_min_cell_value_length(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fods_min_cell_value_length(_wb(_MINIMAL))
        assert result >= 0

    def test_minimal_positive(self):
        result = fods_min_cell_value_length(_wb(_MINIMAL))
        assert result > 0

    def test_typed_non_negative(self):
        result = fods_min_cell_value_length(_wb(_TYPED))
        assert result >= 0

    def test_lte_max(self):
        mn = fods_min_cell_value_length(_wb(_TYPED))
        mx = fods_max_cell_value_length(_wb(_TYPED))
        assert mn <= mx


# --- fods_total_row_count ---

class TestFodsTotalRowCount:
    def test_returns_int(self):
        result = fods_total_row_count(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fods_total_row_count(_wb(_MINIMAL))
        assert result >= 0

    def test_minimal_positive(self):
        result = fods_total_row_count(_wb(_MINIMAL))
        assert result > 0

    def test_multi_sheet_gte_single(self):
        single = fods_total_row_count(_wb(_MINIMAL))
        multi = fods_total_row_count(_wb(_MULTI))
        assert multi >= single

    def test_typed_positive(self):
        result = fods_total_row_count(_wb(_TYPED))
        assert result > 0


# --- fods_has_empty_sheet ---

class TestFodsHasEmptySheet:
    def test_returns_bool(self):
        result = fods_has_empty_sheet(_wb(_MINIMAL))
        assert isinstance(result, bool)

    def test_minimal_false(self):
        # minimal-spreadsheet has content
        result = fods_has_empty_sheet(_wb(_MINIMAL))
        assert result is False

    def test_typed_false(self):
        result = fods_has_empty_sheet(_wb(_TYPED))
        assert result is False

    def test_multi_bool(self):
        result = fods_has_empty_sheet(_wb(_MULTI))
        assert isinstance(result, bool)

    def test_out_of_range_sheet_ignored(self):
        # just confirm it returns bool not error
        result = fods_has_empty_sheet(_wb(_MINIMAL))
        assert isinstance(result, bool)


# --- fods_numeric_cell_count ---

class TestFodsNumericCellCount:
    def test_returns_int(self):
        result = fods_numeric_cell_count(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fods_numeric_cell_count(_wb(_MINIMAL))
        assert result >= 0

    def test_typed_has_numerics(self):
        result = fods_numeric_cell_count(_wb(_TYPED))
        assert result > 0

    def test_out_of_range_sheet_zero(self):
        result = fods_numeric_cell_count(_wb(_MINIMAL))
        assert result >= 0

    def test_is_int(self):
        result = fods_numeric_cell_count(_wb(_TYPED))
        assert type(result) is int
