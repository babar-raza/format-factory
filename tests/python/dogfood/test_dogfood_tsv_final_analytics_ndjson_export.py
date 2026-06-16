"""
Dogfood pipeline: TSV final analytics → NDJSON export.
Covers: tsv_max_numeric_value, tsv_has_empty_rows, tsv_is_rectangular,
        tsv_empty_cell_count, unique_column_values, merge_tsv
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    write_tsv,
    tsv_max_numeric_value,
    tsv_has_empty_rows,
    tsv_is_rectangular,
    tsv_empty_cell_count,
    unique_column_values,
    merge_tsv,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SAMPLE_DIR = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def numeric_tsv(tmp_path):
    rows = [["1", "Alice", "95.5"], ["2", "Bob", "82.0"], ["3", "Carol", "70.0"]]
    dest = tmp_path / "numeric.tsv"
    write_tsv(rows, str(dest), headers=["id", "name", "score"])
    return dest


def test_tsv_max_numeric_value(numeric_tsv, tmp_path):
    max_val = tsv_max_numeric_value(str(numeric_tsv))
    assert max_val is not None
    assert isinstance(max_val, (int, float))
    assert abs(max_val - 95.5) < 1e-6

    record = {"format": "tsv", "function": "tsv_max_numeric_value", "max": max_val}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert abs(loaded[0]["max"] - 95.5) < 1e-6
    assert json.dumps(loaded[0]) is not None


def test_tsv_has_empty_rows(numeric_tsv, tmp_path):
    has_empty = tsv_has_empty_rows(str(numeric_tsv))
    assert isinstance(has_empty, bool)
    assert has_empty is False  # numeric_tsv has no empty rows

    record = {"format": "tsv", "function": "tsv_has_empty_rows", "has_empty": has_empty}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_empty"] is False
    assert json.dumps(loaded[0]) is not None


def test_tsv_is_rectangular(numeric_tsv, tmp_path):
    is_rect = tsv_is_rectangular(str(numeric_tsv))
    assert isinstance(is_rect, bool)
    assert is_rect is True  # all rows have same column count

    record = {"format": "tsv", "function": "tsv_is_rectangular", "is_rectangular": is_rect}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["is_rectangular"] is True
    assert json.dumps(loaded[0]) is not None


def test_tsv_empty_cell_count(numeric_tsv, tmp_path):
    count = tsv_empty_cell_count(str(numeric_tsv))
    assert isinstance(count, int)
    assert count >= 0
    assert count == 0  # numeric_tsv has no empty cells

    record = {"format": "tsv", "function": "tsv_empty_cell_count", "empty_cells": count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["empty_cells"] == 0
    assert json.dumps(loaded[0]) is not None


def test_unique_column_values(numeric_tsv, tmp_path):
    values = unique_column_values(str(numeric_tsv), "name")
    assert isinstance(values, list)
    assert "Alice" in values
    assert "Bob" in values
    assert "Carol" in values
    assert len(values) == 3  # all unique names

    record = {"format": "tsv", "function": "unique_column_values", "col": "name", "count": len(values)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_merge_tsv_doubles_rows(numeric_tsv, tmp_path):
    merged = merge_tsv(str(numeric_tsv), str(numeric_tsv))
    assert isinstance(merged, dict)
    assert "row_count" in merged or "rows" in merged
    row_count = merged.get("row_count") or len(merged.get("rows", []))
    assert row_count == 6  # 3 rows merged with itself = 6

    record = {"format": "tsv", "function": "merge_tsv", "merged_rows": row_count}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["merged_rows"] == 6
    assert json.dumps(loaded[0]) is not None
