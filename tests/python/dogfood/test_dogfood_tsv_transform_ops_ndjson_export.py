"""
Dogfood pipeline: TSV transform ops → NDJSON export.
Covers: sort_rows, filter_rows, append_row, get_row_by_key, sample_rows, find_rows_containing
"""
from __future__ import annotations
import json
import shutil
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    write_tsv,
    sort_rows,
    filter_rows,
    append_row,
    get_row_by_key,
    sample_rows,
    find_rows_containing,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SAMPLE_DIR = _REPO / "samples" / "by-format" / "tsv"


@pytest.fixture
def tsv_file(tmp_path):
    rows = [["1", "Alice", "95.5"], ["2", "Bob", "82.0"], ["3", "Carol", "70.0"]]
    dest = tmp_path / "data.tsv"
    write_tsv(rows, str(dest), headers=["id", "name", "score"])
    return dest


def test_sort_rows_returns_dict(tsv_file, tmp_path):
    result = sort_rows(str(tsv_file), "score", reverse=True)
    assert isinstance(result, dict)
    assert "rows" in result
    # First row should have highest score after reverse sort
    assert result["rows"][0][2] == "95.5"

    record = {"format": "tsv", "function": "sort_rows", "col": "score", "reverse": True, "first_val": result["rows"][0][2]}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["first_val"] == "95.5"
    assert json.dumps(loaded[0]) is not None


def test_filter_rows_returns_matching(tsv_file, tmp_path):
    result = filter_rows(str(tsv_file), "name", "Alice")
    assert isinstance(result, dict)
    assert "rows" in result
    assert len(result["rows"]) == 1
    assert result["rows"][0][1] == "Alice"

    record = {"format": "tsv", "function": "filter_rows", "col": "name", "value": "Alice", "count": len(result["rows"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 1
    assert json.dumps(loaded[0]) is not None


def test_append_row_adds_to_file(tsv_file, tmp_path):
    original_lines = tsv_file.read_text().strip().split("\n")
    append_row(str(tsv_file), ["4", "Dave", "88.0"])
    new_lines = tsv_file.read_text().strip().split("\n")
    assert len(new_lines) == len(original_lines) + 1
    assert "Dave" in tsv_file.read_text()

    record = {"format": "tsv", "function": "append_row", "rows_before": len(original_lines) - 1, "rows_after": len(new_lines) - 1}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rows_after"] == loaded[0]["rows_before"] + 1
    assert json.dumps(loaded[0]) is not None


def test_get_row_by_key_returns_matching_row(tsv_file, tmp_path):
    row = get_row_by_key(str(tsv_file), "name", "Bob")
    assert isinstance(row, list)
    assert row[1] == "Bob"
    assert row[2] == "82.0"

    record = {"format": "tsv", "function": "get_row_by_key", "key_col": "name", "key_val": "Bob", "found": row is not None}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["found"] is True
    assert json.dumps(loaded[0]) is not None


def test_sample_rows_returns_dict(tsv_file, tmp_path):
    result = sample_rows(str(tsv_file), 2)
    assert isinstance(result, dict)
    assert "rows" in result
    assert len(result["rows"]) <= 2

    record = {"format": "tsv", "function": "sample_rows", "n": 2, "returned": len(result["rows"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["returned"] <= 2
    assert json.dumps(loaded[0]) is not None


def test_find_rows_containing_returns_indices(tsv_file, tmp_path):
    indices = find_rows_containing(str(tsv_file), "Carol")
    assert isinstance(indices, list)
    assert len(indices) >= 1
    # Carol is in row index 2 (0-based)
    assert 2 in indices

    record = {"format": "tsv", "function": "find_rows_containing", "text": "Carol", "indices": indices}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert 2 in loaded[0]["indices"]
    assert json.dumps(loaded[0]) is not None
