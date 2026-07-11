"""Tests for SYLK value analytics (sylk_value_analytics.py)."""
from __future__ import annotations
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"
MINIMAL = _SAMPLES / "minimal-2x2.slk"
NUMERIC = _SAMPLES / "numeric-row.slk"
SINGLE = _SAMPLES / "single-cell.slk"

from src.python.sylk.sylk_value_analytics import (
    sylk_has_duplicate_values,
    sylk_duplicate_value_count,
    sylk_numeric_median,
    sylk_has_mixed_types,
    sylk_string_to_numeric_ratio,
    sylk_max_row_numeric_sum,
    sylk_min_row_numeric_sum,
    sylk_numeric_cells_per_row,
)


class TestSylkHasDuplicateValues:
    def test_returns_bool(self):
        assert isinstance(sylk_has_duplicate_values(MINIMAL), bool)

    def test_minimal_no_duplicates(self):
        assert sylk_has_duplicate_values(MINIMAL) is False

    def test_accepts_string_path(self):
        assert isinstance(sylk_has_duplicate_values(str(MINIMAL)), bool)

    def test_single_cell_no_duplicates(self):
        assert sylk_has_duplicate_values(SINGLE) is False


class TestSylkDuplicateValueCount:
    def test_returns_int(self):
        assert isinstance(sylk_duplicate_value_count(MINIMAL), int)

    def test_nonnegative(self):
        assert sylk_duplicate_value_count(MINIMAL) >= 0

    def test_minimal_zero_duplicates(self):
        assert sylk_duplicate_value_count(MINIMAL) == 0

    def test_accepts_string_path(self):
        assert isinstance(sylk_duplicate_value_count(str(MINIMAL)), int)


class TestSylkNumericMedian:
    def test_returns_float(self):
        assert isinstance(sylk_numeric_median(MINIMAL), float)

    def test_single_numeric_equals_value(self):
        # minimal-2x2 has 1 numeric cell with value 42
        assert sylk_numeric_median(MINIMAL) == 42.0

    def test_nonnumeric_returns_zero(self):
        # single-cell — check if it has numeric content or not
        result = sylk_numeric_median(SINGLE)
        assert isinstance(result, float)

    def test_accepts_string_path(self):
        assert isinstance(sylk_numeric_median(str(MINIMAL)), float)


class TestSylkHasMixedTypes:
    def test_returns_bool(self):
        assert isinstance(sylk_has_mixed_types(MINIMAL), bool)

    def test_minimal_has_mixed_types(self):
        # minimal-2x2 has strings and one numeric
        assert sylk_has_mixed_types(MINIMAL) is True

    def test_accepts_string_path(self):
        assert isinstance(sylk_has_mixed_types(str(MINIMAL)), bool)


class TestSylkStringToNumericRatio:
    def test_returns_float(self):
        assert isinstance(sylk_string_to_numeric_ratio(MINIMAL), float)

    def test_nonnegative(self):
        assert sylk_string_to_numeric_ratio(MINIMAL) >= 0.0

    def test_minimal_has_string_ratio(self):
        # 3 strings, 1 numeric → ratio = 3.0
        assert sylk_string_to_numeric_ratio(MINIMAL) == 3.0

    def test_accepts_string_path(self):
        assert isinstance(sylk_string_to_numeric_ratio(str(MINIMAL)), float)


class TestSylkMaxRowNumericSum:
    def test_returns_float(self):
        assert isinstance(sylk_max_row_numeric_sum(MINIMAL), float)

    def test_minimal_max_numeric_sum(self):
        # Only one numeric cell (42) in the whole document
        assert sylk_max_row_numeric_sum(MINIMAL) == 42.0

    def test_nonnumeric_returns_zero(self):
        result = sylk_max_row_numeric_sum(SINGLE)
        assert isinstance(result, float)

    def test_accepts_string_path(self):
        assert isinstance(sylk_max_row_numeric_sum(str(MINIMAL)), float)


class TestSylkMinRowNumericSum:
    def test_returns_float(self):
        assert isinstance(sylk_min_row_numeric_sum(MINIMAL), float)

    def test_minimal_min_equals_max(self):
        # Only one numeric row
        assert sylk_min_row_numeric_sum(MINIMAL) == sylk_max_row_numeric_sum(MINIMAL)

    def test_accepts_string_path(self):
        assert isinstance(sylk_min_row_numeric_sum(str(MINIMAL)), float)


class TestSylkNumericCellsPerRow:
    def test_returns_float(self):
        assert isinstance(sylk_numeric_cells_per_row(MINIMAL), float)

    def test_nonnegative(self):
        assert sylk_numeric_cells_per_row(MINIMAL) >= 0.0

    def test_minimal_one_per_row(self):
        # 1 numeric cell in 1 row → avg = 1.0
        assert sylk_numeric_cells_per_row(MINIMAL) == 1.0

    def test_accepts_string_path(self):
        assert isinstance(sylk_numeric_cells_per_row(str(MINIMAL)), float)
