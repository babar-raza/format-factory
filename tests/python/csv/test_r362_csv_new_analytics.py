"""
Sprint 98 — CSV analytics round 4.
25 tests for 5 new analytics functions:
  csv_total_field_count, csv_numeric_field_ratio, csv_max_field_value_length,
  csv_nonempty_field_count, csv_row_count
"""
import sys
import pytest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_total_field_count,
    csv_numeric_field_ratio,
    csv_max_field_value_length,
    csv_nonempty_field_count,
    csv_row_count,
)

_SAMPLES = _REPO / "samples" / "by-format" / "csv"
_MINIMAL = str(_SAMPLES / "minimal-2x2.csv")
_SINGLE = str(_SAMPLES / "single-cell.csv")
_QUOTED = str(_SAMPLES / "quoted-fields.csv")


# --- csv_total_field_count ---

class TestCsvTotalFieldCount:
    def test_returns_int(self):
        result = csv_total_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_total_field_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = csv_total_field_count(_MINIMAL)
        assert result > 0

    def test_single_cell_is_one(self):
        result = csv_total_field_count(_SINGLE)
        assert result >= 1

    def test_quoted_positive(self):
        result = csv_total_field_count(_QUOTED)
        assert result > 0


# --- csv_numeric_field_ratio ---

class TestCsvNumericFieldRatio:
    def test_returns_float(self):
        result = csv_numeric_field_ratio(_MINIMAL)
        assert isinstance(result, float)

    def test_bounded_0_to_1(self):
        result = csv_numeric_field_ratio(_MINIMAL)
        assert 0.0 <= result <= 1.0

    def test_single_cell_bounded(self):
        result = csv_numeric_field_ratio(_SINGLE)
        assert 0.0 <= result <= 1.0

    def test_quoted_bounded(self):
        result = csv_numeric_field_ratio(_QUOTED)
        assert 0.0 <= result <= 1.0

    def test_all_samples_bounded(self):
        for path in [_MINIMAL, _SINGLE, _QUOTED]:
            r = csv_numeric_field_ratio(path)
            assert 0.0 <= r <= 1.0


# --- csv_max_field_value_length ---

class TestCsvMaxFieldValueLength:
    def test_returns_int(self):
        result = csv_max_field_value_length(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_max_field_value_length(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = csv_max_field_value_length(_MINIMAL)
        assert result > 0

    def test_single_cell_non_negative(self):
        result = csv_max_field_value_length(_SINGLE)
        assert result >= 0

    def test_quoted_positive(self):
        result = csv_max_field_value_length(_QUOTED)
        assert result > 0


# --- csv_nonempty_field_count ---

class TestCsvNonemptyFieldCount:
    def test_returns_int(self):
        result = csv_nonempty_field_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_nonempty_field_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = csv_nonempty_field_count(_MINIMAL)
        assert result > 0

    def test_single_cell_gte_one(self):
        result = csv_nonempty_field_count(_SINGLE)
        assert result >= 1

    def test_lte_total_field_count(self):
        nonempty = csv_nonempty_field_count(_QUOTED)
        total = csv_total_field_count(_QUOTED)
        assert nonempty <= total


# --- csv_row_count ---

class TestCsvRowCount:
    def test_returns_int(self):
        result = csv_row_count(_MINIMAL)
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_row_count(_MINIMAL)
        assert result >= 0

    def test_minimal_positive(self):
        result = csv_row_count(_MINIMAL)
        assert result > 0

    def test_single_cell_is_one(self):
        result = csv_row_count(_SINGLE)
        assert result >= 1

    def test_quoted_positive(self):
        result = csv_row_count(_QUOTED)
        assert result > 0
