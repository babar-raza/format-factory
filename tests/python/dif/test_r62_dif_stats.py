"""
test_r62_dif_stats.py — R62 Train I: DIF stats API tests.

Tests the two new capability functions added to src/python/dif/dif_stats.py:
  - dif_stats(): aggregate row/cell/type statistics
  - dif_numeric_range(): min/max/count of numeric values

R62 Sprint: FORMAT-FACTORY-R62-AI-ACCELERATED-DELIVERED-SIDECAR-PYTHON-RC-PHASE13-MEGA-TRAIN-001
"""
from __future__ import annotations

import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(PROJECT_ROOT / "src" / "python"))

from dif.dif_stats import dif_stats, dif_numeric_range


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _num_cell(value):
    return {"value": value, "type": "numeric"}


def _str_cell(value):
    return {"value": value, "type": "string"}


def _doc(rows=None, title="TEST", vectors=0, tuples=0):
    return {
        "ok": True,
        "title": title,
        "vectors": vectors,
        "tuples": tuples,
        "row_count": len(rows) if rows else 0,
        "rows": rows or [],
    }


# ---------------------------------------------------------------------------
# dif_stats
# ---------------------------------------------------------------------------

class TestDifStatsEmpty:
    def test_empty_doc_returns_zeros(self):
        result = dif_stats(_doc())
        assert result["row_count"] == 0
        assert result["total_cells"] == 0
        assert result["numeric_cells"] == 0
        assert result["string_cells"] == 0

    def test_returns_dict(self):
        assert isinstance(dif_stats(_doc()), dict)

    def test_has_required_keys(self):
        result = dif_stats(_doc())
        for key in ("row_count", "vectors", "tuples", "total_cells",
                    "numeric_cells", "string_cells", "empty_cells", "title"):
            assert key in result, f"Missing key: {key}"

    def test_title_preserved(self):
        result = dif_stats(_doc(title="SALES"))
        assert result["title"] == "SALES"

    def test_vectors_tuples_preserved(self):
        result = dif_stats(_doc(vectors=5, tuples=3))
        assert result["vectors"] == 5
        assert result["tuples"] == 3


class TestDifStatsContent:
    def test_single_numeric_cell(self):
        result = dif_stats(_doc(rows=[[_num_cell(42)]]))
        assert result["numeric_cells"] == 1
        assert result["total_cells"] == 1

    def test_single_string_cell(self):
        result = dif_stats(_doc(rows=[[_str_cell("hello")]]))
        assert result["string_cells"] == 1

    def test_mixed_row(self):
        row = [_num_cell(1), _str_cell("x"), _num_cell(2)]
        result = dif_stats(_doc(rows=[row]))
        assert result["numeric_cells"] == 2
        assert result["string_cells"] == 1
        assert result["total_cells"] == 3

    def test_multiple_rows(self):
        rows = [
            [_num_cell(1.0), _num_cell(2.0)],
            [_str_cell("a"), _str_cell("b")],
        ]
        result = dif_stats(_doc(rows=rows))
        assert result["row_count"] == 2
        assert result["numeric_cells"] == 2
        assert result["string_cells"] == 2
        assert result["total_cells"] == 4


# ---------------------------------------------------------------------------
# dif_numeric_range
# ---------------------------------------------------------------------------

class TestDifNumericRange:
    def test_empty_doc_returns_nones(self):
        result = dif_numeric_range(_doc())
        assert result["min_value"] is None
        assert result["max_value"] is None
        assert result["numeric_count"] == 0

    def test_single_numeric_value(self):
        result = dif_numeric_range(_doc(rows=[[_num_cell(5.0)]]))
        assert result["min_value"] == 5.0
        assert result["max_value"] == 5.0
        assert result["numeric_count"] == 1

    def test_multiple_values_range(self):
        rows = [[_num_cell(3), _num_cell(7), _num_cell(1)]]
        result = dif_numeric_range(_doc(rows=rows))
        assert result["min_value"] == 1.0
        assert result["max_value"] == 7.0
        assert result["numeric_count"] == 3

    def test_string_cells_ignored(self):
        rows = [[_str_cell("x"), _num_cell(10), _str_cell("y")]]
        result = dif_numeric_range(_doc(rows=rows))
        assert result["numeric_count"] == 1
        assert result["max_value"] == 10.0

    def test_returns_dict(self):
        assert isinstance(dif_numeric_range(_doc()), dict)

    def test_has_required_keys(self):
        result = dif_numeric_range(_doc())
        for key in ("min_value", "max_value", "numeric_count"):
            assert key in result, f"Missing key: {key}"
