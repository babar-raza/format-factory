"""
tests/python/csv/test_r187_csv_column_count.py

Sprint: FORMAT-FACTORY-PRODUCT-DEEPENING-RNEXT55-001
Tests for csv_column_count() — number of columns in the CSV file.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ff_csv.csv_parser import csv_column_count

SAMPLES = _REPO / "samples" / "by-format" / "csv"


class TestCsvColumnCount:
    def test_single_cell_is_one(self):
        result = csv_column_count(SAMPLES / "single-cell.csv")
        assert result == 1

    def test_minimal_2x2_is_two(self):
        result = csv_column_count(SAMPLES / "minimal-2x2.csv")
        assert result == 2

    def test_quoted_fields_is_three(self):
        result = csv_column_count(SAMPLES / "quoted-fields.csv")
        assert result == 3

    def test_returns_int(self):
        result = csv_column_count(SAMPLES / "single-cell.csv")
        assert isinstance(result, int)

    def test_non_negative(self):
        result = csv_column_count(SAMPLES / "minimal-2x2.csv")
        assert result >= 0

    def test_exported_from_init(self):
        from src.python.ff_csv import csv_column_count as fn
        result = fn(SAMPLES / "minimal-2x2.csv")
        assert result == 2
