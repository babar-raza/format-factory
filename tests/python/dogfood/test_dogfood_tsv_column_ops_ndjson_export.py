"""
Dogfood pipeline: TSV column manipulation ops → NDJSON export.
Covers: append_rows, drop_column, add_column, rename_column, get_column_values,
        get_numeric_columns (6 tests)
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
    append_rows,
    drop_column,
    add_column,
    rename_column,
    get_column_values,
    get_numeric_columns,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SAMPLE_DIR = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def tsv_file(tmp_path):
    rows = [["1", "Alice", "95.5"], ["2", "Bob", "82.0"]]
    dest = tmp_path / "data.tsv"
    write_tsv(rows, str(dest), headers=["id", "name", "score"])
    return dest


def test_append_rows_increases_count(tsv_file, tmp_path):
    result = append_rows(str(tsv_file), [["3", "Carol", "70.0"]])
    assert isinstance(result, dict)
    assert result["row_count"] == 3

    record = {"format": "tsv", "function": "append_rows", "new_row_count": result["row_count"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["new_row_count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_drop_column_removes_header(tsv_file, tmp_path):
    result = drop_column(str(tsv_file), "score")
    assert isinstance(result, dict)
    assert "score" not in result["headers"]
    assert "id" in result["headers"]
    assert "name" in result["headers"]

    record = {"format": "tsv", "function": "drop_column", "col": "score", "remaining_headers": result["headers"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "score" not in loaded[0]["remaining_headers"]
    assert json.dumps(loaded[0]) is not None


def test_add_column_adds_header(tsv_file, tmp_path):
    result = add_column(str(tsv_file), "grade", ["A", "B"])
    assert isinstance(result, dict)
    assert "grade" in result["headers"]
    assert len(result["headers"]) == 4  # id, name, score, grade

    record = {"format": "tsv", "function": "add_column", "new_col": "grade", "header_count": len(result["headers"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["header_count"] == 4
    assert json.dumps(loaded[0]) is not None


def test_rename_column_changes_name(tsv_file, tmp_path):
    result = rename_column(str(tsv_file), "score", "points")
    assert isinstance(result, dict)
    assert "points" in result["headers"]
    assert "score" not in result["headers"]

    record = {"format": "tsv", "function": "rename_column", "old": "score", "new": "points", "headers": result["headers"]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "points" in loaded[0]["headers"]
    assert "score" not in loaded[0]["headers"]
    assert json.dumps(loaded[0]) is not None


def test_get_column_values_returns_list(tsv_file, tmp_path):
    values = get_column_values(str(tsv_file), "name")
    assert isinstance(values, list)
    assert "Alice" in values
    assert "Bob" in values

    record = {"format": "tsv", "function": "get_column_values", "col": "name", "values": values}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "Alice" in loaded[0]["values"]
    assert json.dumps(loaded[0]) is not None


def test_get_numeric_columns_returns_list(tsv_file, tmp_path):
    numeric_cols = get_numeric_columns(str(tsv_file))
    assert isinstance(numeric_cols, list)
    assert "score" in numeric_cols
    assert "id" in numeric_cols
    # 'name' column should NOT be numeric
    assert "name" not in numeric_cols

    record = {"format": "tsv", "function": "get_numeric_columns", "numeric_cols": numeric_cols, "count": len(numeric_cols)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert "score" in loaded[0]["numeric_cols"]
    assert json.dumps(loaded[0]) is not None
