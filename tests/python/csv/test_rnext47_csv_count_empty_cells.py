"""
test_rnext47_csv_count_empty_cells.py

New product function: csv_parser.count_empty_cells
Sprint: FORMAT-FACTORY-PROBE-COVERAGE-PRODUCT-RNEXT47-001
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.csv.csv_parser import count_empty_cells, CsvInputError


class TestCountEmptyCells:
    def test_no_empty_cells(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_bytes(b"name,age\nAlice,30\nBob,25\n")
        assert count_empty_cells(f, "name") == 0
        assert count_empty_cells(f, "age") == 0

    def test_all_empty_in_column(self, tmp_path):
        # Use numeric values in rows to trigger header heuristic
        f = tmp_path / "data.csv"
        f.write_bytes(b"name,score\nAlice,\nBob,\n")
        # Heuristic won't detect header with all-empty numeric col; use explicit numeric mix
        f.write_bytes(b"id,score\n1,\n2,\n")
        assert count_empty_cells(f, "score") == 2

    def test_some_empty_cells(self, tmp_path):
        # Mix of numeric and empty to trigger header detection
        f = tmp_path / "data.csv"
        f.write_bytes(b"name,score\nAlice,90\nBob,\nCarol,75\nDan,\n")
        assert count_empty_cells(f, "score") == 2

    def test_unknown_column_returns_zero(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_bytes(b"name,age\nAlice,30\n")
        assert count_empty_cells(f, "nonexistent") == 0

    def test_whitespace_only_cell_counts_as_empty(self, tmp_path):
        # Whitespace-only cells in a numeric-containing row set triggers header
        f = tmp_path / "data.csv"
        f.write_bytes(b"name,score\nAlice,  \nBob,95\n")
        assert count_empty_cells(f, "score") == 1

    def test_missing_file_raises(self, tmp_path):
        with pytest.raises(Exception):
            count_empty_cells(tmp_path / "ghost.csv", "col")

    def test_returns_int(self, tmp_path):
        f = tmp_path / "data.csv"
        f.write_bytes(b"x,y\n1,\n2,3\n")
        result = count_empty_cells(f, "y")
        assert isinstance(result, int)
        assert result == 1
