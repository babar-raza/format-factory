"""
test_r66_csv_advancement.py -- R66 Train I: CSV format track advancement.

New capability: csv_max_field_length(rows) -> int

R66 Sprint: FORMAT-FACTORY-R66 product advancement
Train I -- CSV format track advancement

NOTE: Uses PROJECT_ROOT sys.path pattern to avoid stdlib csv shadowing.
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.ff_csv.csv_stats import csv_max_field_length


# ---------------------------------------------------------------------------
# csv_max_field_length tests
# ---------------------------------------------------------------------------

class TestCsvMaxFieldLength:
    """Tests for csv_max_field_length()."""

    def test_empty_rows_returns_zero(self):
        result = csv_max_field_length([])
        assert result == 0

    def test_returns_int(self):
        result = csv_max_field_length([])
        assert isinstance(result, int)

    def test_single_field(self):
        result = csv_max_field_length([["hello"]])
        assert result == 5

    def test_multiple_fields_returns_max(self):
        rows = [
            ["a", "bb", "ccc"],
            ["dddd", "ee"],
        ]
        result = csv_max_field_length(rows)
        assert result == 4

    def test_none_fields_skipped(self):
        rows = [[None, "abc", None]]
        result = csv_max_field_length(rows)
        assert result == 3

    def test_numeric_fields_converted_to_string(self):
        rows = [[12345, 1.5]]
        result = csv_max_field_length(rows)
        assert result == 5  # "12345"

    def test_all_none_returns_zero(self):
        rows = [[None, None], [None]]
        result = csv_max_field_length(rows)
        assert result == 0

    def test_empty_string_field(self):
        rows = [["", "x"]]
        result = csv_max_field_length(rows)
        assert result == 1
