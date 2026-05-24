"""
test_r62_csv_stats.py — R62 Train I: CSV stats API tests.

Tests the two new capability functions added to src/python/csv/csv_stats.py:
  - table_stats(): aggregate row/column/cell statistics
  - column_value_counts(): distinct value frequency per column

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT))

from src.python.csv.csv_stats import table_stats, column_value_counts


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _doc(rows=None, headers=None, has_header=False, column_count=0, delimiter=","):
    return {
        "format": "csv",
        "row_count": len(rows) if rows else 0,
        "column_count": column_count or (len(rows[0]) if rows else 0),
        "headers": headers,
        "rows": rows or [],
        "has_header": has_header,
        "delimiter": delimiter,
    }


# ---------------------------------------------------------------------------
# table_stats
# ---------------------------------------------------------------------------

class TestTableStatsEmpty:
    def test_empty_doc_returns_zeros(self):
        result = table_stats(_doc())
        assert result["row_count"] == 0
        assert result["total_cells"] == 0
        assert result["non_empty_cells"] == 0

    def test_returns_dict(self):
        assert isinstance(table_stats(_doc()), dict)

    def test_has_required_keys(self):
        result = table_stats(_doc())
        for key in ("row_count", "column_count", "has_header", "header_names",
                    "total_cells", "non_empty_cells", "empty_cell_count", "delimiter"):
            assert key in result, f"Missing key: {key}"

    def test_no_header_returns_none_for_header_names(self):
        result = table_stats(_doc(rows=[["a", "b"]], has_header=False))
        assert result["header_names"] is None


class TestTableStatsContent:
    def test_single_row(self):
        result = table_stats(_doc(rows=[["x", "y", "z"]], column_count=3))
        assert result["row_count"] == 1
        assert result["total_cells"] == 3

    def test_multi_row(self):
        rows = [["a", "b"], ["c", "d"], ["e", "f"]]
        result = table_stats(_doc(rows=rows, column_count=2))
        assert result["row_count"] == 3
        assert result["total_cells"] == 6

    def test_empty_cells_counted(self):
        rows = [["a", ""], ["", "b"]]
        result = table_stats(_doc(rows=rows, column_count=2))
        assert result["empty_cell_count"] == 2
        assert result["non_empty_cells"] == 2

    def test_with_header(self):
        result = table_stats(_doc(
            rows=[["alice", "30"]],
            headers=["name", "age"],
            has_header=True,
            column_count=2,
        ))
        assert result["has_header"] is True
        assert result["header_names"] == ["name", "age"]

    def test_delimiter_preserved(self):
        result = table_stats(_doc(rows=[["a", "b"]], delimiter="\t"))
        assert result["delimiter"] == "\t"

    def test_total_cells_equals_rows_times_cols(self):
        rows = [["a", "b", "c"] for _ in range(5)]
        result = table_stats(_doc(rows=rows, column_count=3))
        assert result["total_cells"] == 15


# ---------------------------------------------------------------------------
# column_value_counts
# ---------------------------------------------------------------------------

class TestColumnValueCounts:
    def test_empty_rows_returns_empty(self):
        result = column_value_counts(_doc(), 0)
        assert result == {}

    def test_single_column_single_value(self):
        result = column_value_counts(_doc(rows=[["alice"]]), 0)
        assert result == {"alice": 1}

    def test_count_distinct_values(self):
        rows = [["a"], ["b"], ["a"], ["c"], ["a"]]
        result = column_value_counts(_doc(rows=rows), 0)
        assert result["a"] == 3
        assert result["b"] == 1
        assert result["c"] == 1

    def test_column_index_1(self):
        rows = [["x", "y"], ["x", "z"], ["x", "y"]]
        result = column_value_counts(_doc(rows=rows, column_count=2), 1)
        assert result["y"] == 2
        assert result["z"] == 1

    def test_out_of_bounds_column_counts_empty_string(self):
        rows = [["a"], ["b"]]
        result = column_value_counts(_doc(rows=rows), 5)
        assert result == {"": 2}
