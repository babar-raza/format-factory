"""Tests for sylk_unique_values().

Sprint: FORMAT-FACTORY-FORCED-PLAN-EXECUTION-20260613
Taskcard: FOSS-SYLK-UNIQUE-VALUES-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.sylk.sylk_parser import sylk_unique_values

SYLK_SAMPLES = _REPO / "samples" / "by-format" / "sylk" / "valid"


class TestSylkUniqueValuesBasic:
    def test_import(self):
        assert callable(sylk_unique_values)

    def test_returns_list(self):
        result = sylk_unique_values(SYLK_SAMPLES / "minimal-2x2.slk", 1)
        assert isinstance(result, list)

    def test_minimal_col1_has_two_unique_strings(self):
        # minimal-2x2.slk col 1: "Name", "Alpha"
        result = sylk_unique_values(SYLK_SAMPLES / "minimal-2x2.slk", 1)
        assert len(result) == 2
        assert "Alpha" in result
        assert "Name" in result

    def test_minimal_col1_is_sorted(self):
        # alphabetically: "Alpha" before "Name"
        result = sylk_unique_values(SYLK_SAMPLES / "minimal-2x2.slk", 1)
        assert result == sorted(result, key=str)

    def test_single_cell_col1_one_value(self):
        # single-cell.slk col 1: 99
        result = sylk_unique_values(SYLK_SAMPLES / "single-cell.slk", 1)
        assert result == [99]

    def test_numeric_row_each_col_one_value(self):
        # numeric-row.slk: col1=1, col2=2, col3=3
        assert sylk_unique_values(SYLK_SAMPLES / "numeric-row.slk", 1) == [1]
        assert sylk_unique_values(SYLK_SAMPLES / "numeric-row.slk", 2) == [2]
        assert sylk_unique_values(SYLK_SAMPLES / "numeric-row.slk", 3) == [3]

    def test_missing_column_returns_empty_list(self):
        # col 99 does not exist in any sample
        result = sylk_unique_values(SYLK_SAMPLES / "minimal-2x2.slk", 99)
        assert result == []

    def test_duplicate_values_counted_once(self):
        # Create a temporary SYLK file with repeated values and verify dedup
        import tempfile
        import os
        content = "ID;P\nC;X1;Y1;K5\nC;X1;Y2;K5\nC;X1;Y3;K10\nE\n"
        with tempfile.NamedTemporaryFile(
            suffix=".slk", mode="w", delete=False, encoding="ascii"
        ) as f:
            f.write(content)
            tmp = f.name
        try:
            result = sylk_unique_values(tmp, 1)
            assert result == [5, 10]
        finally:
            os.unlink(tmp)
