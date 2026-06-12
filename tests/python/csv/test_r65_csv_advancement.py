"""
test_r65_csv_advancement.py -- R65 Train I: CSV format track advancement.

New capability: csv_empty_row_count(rows) -- count of rows where all fields are empty.

IMPORTANT: Does NOT `import csv` at module level (src/python/csv/ shadows stdlib csv).

R65 Sprint: Train I -- CSV stats module expansion
"""
from __future__ import annotations

import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.csv.csv_stats import csv_empty_row_count


# ---------------------------------------------------------------------------
# csv_empty_row_count tests
# ---------------------------------------------------------------------------

class TestCsvEmptyRowCount:
    """Tests for csv_empty_row_count()."""

    def test_no_rows(self):
        assert csv_empty_row_count([]) == 0

    def test_all_non_empty_rows(self):
        rows = [["a", "b"], ["c", "d"]]
        assert csv_empty_row_count(rows) == 0

    def test_all_empty_rows(self):
        rows = [["", ""], [None, ""], ["", " "]]
        assert csv_empty_row_count(rows) == 3

    def test_mixed_empty_and_non_empty(self):
        rows = [["data", "here"], ["", ""], ["more", "data"]]
        assert csv_empty_row_count(rows) == 1

    def test_whitespace_only_counts_as_empty(self):
        rows = [["  ", "\t", " "]]
        assert csv_empty_row_count(rows) == 1

    def test_none_fields_count_as_empty(self):
        rows = [[None, None]]
        assert csv_empty_row_count(rows) == 1

    def test_empty_inner_list_counts_as_empty(self):
        rows = [[]]
        assert csv_empty_row_count(rows) == 1

    def test_returns_int(self):
        rows = [["x"], ["", ""], ["y"]]
        result = csv_empty_row_count(rows)
        assert isinstance(result, int)
        assert result == 1
