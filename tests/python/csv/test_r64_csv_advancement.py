"""
test_r64_csv_advancement.py -- R64 Train I: CSV format track advancement.

New capability: csv_field_type_summary(rows)
  Returns dict with counts of numeric, empty, and text fields across all rows.

R64 Sprint: Train I -- CSV format track advancement

CRITICAL: src/python/csv/ shadows stdlib csv. Use PROJECT_ROOT import path.
"""
from __future__ import annotations
import sys
from pathlib import Path
import pytest

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))
from src.python.csv.csv_stats import csv_field_type_summary


class TestCsvFieldTypeSummary:
    def test_empty_rows(self):
        result = csv_field_type_summary([])
        assert result == {"numeric": 0, "empty": 0, "text": 0}

    def test_all_numeric(self):
        rows = [["1", "2.5", "3"], ["4", "-1.0", "0"]]
        result = csv_field_type_summary(rows)
        assert result["numeric"] == 6
        assert result["text"] == 0
        assert result["empty"] == 0

    def test_all_text(self):
        rows = [["hello", "world"], ["foo", "bar"]]
        result = csv_field_type_summary(rows)
        assert result["text"] == 4
        assert result["numeric"] == 0

    def test_empty_fields(self):
        rows = [["", None, "  "], ["", None]]
        result = csv_field_type_summary(rows)
        assert result["empty"] == 5

    def test_mixed_types(self):
        rows = [["42", "hello", ""], ["3.14", None, "world"]]
        result = csv_field_type_summary(rows)
        assert result["numeric"] == 2
        assert result["text"] == 2
        assert result["empty"] == 2

    def test_integer_strings_are_numeric(self):
        rows = [["100", "-5", "0"]]
        result = csv_field_type_summary(rows)
        assert result["numeric"] == 3

    def test_returns_correct_keys(self):
        result = csv_field_type_summary([])
        assert set(result.keys()) == {"numeric", "empty", "text"}

    def test_callable_from_module(self):
        from src.python.csv import csv_stats
        assert callable(csv_stats.csv_field_type_summary)
