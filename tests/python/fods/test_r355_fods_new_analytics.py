"""
Sprint 91 — FODS analytics round 4.
25 tests for 5 new analytics functions:
  fods_value_variance, fods_row_col_ratio, fods_string_length_sum,
  fods_row_fill_rate, fods_cell_entropy
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.fods import (
    parse_fods,
    fods_value_variance,
    fods_row_col_ratio,
    fods_string_length_sum,
    fods_row_fill_rate,
    fods_cell_entropy,
)

_SAMPLES = _REPO / "samples" / "by-format" / "fods"
_MINIMAL = str(_SAMPLES / "minimal-spreadsheet.fods")
_TYPED = str(_SAMPLES / "typed-values-basic.fods")
_MULTI = str(_SAMPLES / "multi-sheet-basic.fods")


def _wb(path):
    return parse_fods(path)


# --- fods_value_variance ---

class TestFodsValueVariance:
    def test_returns_float(self):
        result = fods_value_variance(_wb(_MINIMAL))
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fods_value_variance(_wb(_MINIMAL))
        assert result >= 0.0

    def test_typed_values(self):
        result = fods_value_variance(_wb(_TYPED))
        assert isinstance(result, float) and result >= 0.0

    def test_out_of_range_sheet_is_zero(self):
        result = fods_value_variance(_wb(_MINIMAL), sheet_index=999)
        assert result == 0.0

    def test_multi_sheet(self):
        result = fods_value_variance(_wb(_MULTI))
        assert isinstance(result, float)


# --- fods_row_col_ratio ---

class TestFodsRowColRatio:
    def test_returns_float(self):
        result = fods_row_col_ratio(_wb(_MINIMAL))
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fods_row_col_ratio(_wb(_MINIMAL))
        assert result >= 0.0

    def test_typed_values(self):
        result = fods_row_col_ratio(_wb(_TYPED))
        assert isinstance(result, float) and result >= 0.0

    def test_out_of_range_sheet_is_zero(self):
        result = fods_row_col_ratio(_wb(_MINIMAL), sheet_index=999)
        assert result == 0.0

    def test_multi_sheet(self):
        result = fods_row_col_ratio(_wb(_MULTI))
        assert isinstance(result, float)


# --- fods_string_length_sum ---

class TestFodsStringLengthSum:
    def test_returns_int(self):
        result = fods_string_length_sum(_wb(_MINIMAL))
        assert isinstance(result, int)

    def test_non_negative(self):
        result = fods_string_length_sum(_wb(_MINIMAL))
        assert result >= 0

    def test_typed_values(self):
        result = fods_string_length_sum(_wb(_TYPED))
        assert isinstance(result, int) and result >= 0

    def test_out_of_range_sheet_is_zero(self):
        result = fods_string_length_sum(_wb(_MINIMAL), sheet_index=999)
        assert result == 0

    def test_multi_sheet(self):
        result = fods_string_length_sum(_wb(_MULTI))
        assert isinstance(result, int)


# --- fods_row_fill_rate ---

class TestFodsRowFillRate:
    def test_returns_float(self):
        result = fods_row_fill_rate(_wb(_MINIMAL))
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = fods_row_fill_rate(_wb(_MINIMAL))
        assert 0.0 <= result <= 1.0

    def test_typed_values(self):
        result = fods_row_fill_rate(_wb(_TYPED))
        assert 0.0 <= result <= 1.0

    def test_out_of_range_sheet_is_zero(self):
        result = fods_row_fill_rate(_wb(_MINIMAL), sheet_index=999)
        assert result == 0.0

    def test_multi_sheet(self):
        result = fods_row_fill_rate(_wb(_MULTI))
        assert isinstance(result, float)


# --- fods_cell_entropy ---

class TestFodsCellEntropy:
    def test_returns_float(self):
        result = fods_cell_entropy(_wb(_MINIMAL))
        assert isinstance(result, float)

    def test_non_negative(self):
        result = fods_cell_entropy(_wb(_MINIMAL))
        assert result >= 0.0

    def test_typed_values(self):
        result = fods_cell_entropy(_wb(_TYPED))
        assert isinstance(result, float) and result >= 0.0

    def test_out_of_range_sheet_is_zero(self):
        result = fods_cell_entropy(_wb(_MINIMAL), sheet_index=999)
        assert result == 0.0

    def test_bounded_by_8(self):
        result = fods_cell_entropy(_wb(_TYPED))
        assert result <= 8.0
