"""
tests/python/csv/test_rnext_csv_gap_closure_foss.py

Tests for 3 new CSV analytics functions:
- csv_column_value_set
- csv_field_type_counts
- csv_max_field_length
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import (
    csv_column_value_set,
    csv_field_type_counts,
    csv_max_field_length,
)

_CSV = str(_REPO / "samples" / "by-format" / "csv" / "minimal-2x2.csv")


class TestCsvGapClosureFoss:

    def test_column_value_set_col0(self):
        result = csv_column_value_set(_CSV, 0)
        assert result == ["Alice", "Bob"]

    def test_column_value_set_col1(self):
        result = csv_column_value_set(_CSV, 1)
        assert result == ["25", "30"]

    def test_column_value_set_out_of_range(self):
        result = csv_column_value_set(_CSV, 99)
        assert result == []

    def test_field_type_counts(self):
        result = csv_field_type_counts(_CSV)
        assert result["numeric"] == 2
        assert result["string"] == 2

    def test_field_type_counts_has_keys(self):
        result = csv_field_type_counts(_CSV)
        assert "numeric" in result
        assert "string" in result

    def test_max_field_length(self):
        assert csv_max_field_length(_CSV) == 5

    def test_max_field_length_is_int(self):
        result = csv_max_field_length(_CSV)
        assert isinstance(result, int)
        assert result > 0
