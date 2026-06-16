"""
Dogfood pipeline: TSV utility ops → NDJSON export.
Covers: write_tsv, get_column, get_row, validate_headers, to_csv, deduplicate_rows
"""
from __future__ import annotations
import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import (
    write_tsv,
    get_column,
    get_row,
    validate_headers,
    to_csv,
    deduplicate_rows,
)
from ndjson.ndjson_codec import write_ndjson, load_ndjson

_SAMPLE_DIR = _REPO / "samples" / "by-format" / "tsv"


def _valid_tsv_files():
    return sorted(_SAMPLE_DIR.glob("*.tsv"))


def _make_tsv_file(tmp_path: Path, rows, headers) -> Path:
    dest = tmp_path / "test.tsv"
    write_tsv(rows, str(dest), headers=headers)
    return dest


@pytest.fixture
def tsv_sample(tmp_path):
    rows = [["1", "Alice", "95.5"], ["2", "Bob", "82.0"], ["2", "Bob", "82.0"]]
    return _make_tsv_file(tmp_path, rows, headers=["id", "name", "score"])


def test_write_tsv_produces_valid_file(tmp_path):
    rows = [["10", "Carol", "77.5"], ["20", "Dave", "88.0"]]
    dest = tmp_path / "out.tsv"
    write_tsv(rows, str(dest), headers=["id", "name", "score"])
    assert dest.exists()
    content = dest.read_text()
    assert "Carol" in content
    assert "Dave" in content

    record = {"format": "tsv", "function": "write_tsv", "rows": len(rows), "has_headers": True}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["rows"] == 2
    assert json.dumps(loaded[0]) is not None


def test_get_column_returns_list(tsv_sample, tmp_path):
    col = get_column(str(tsv_sample), "name")
    assert isinstance(col, list)
    assert "Alice" in col
    assert "Bob" in col

    record = {"format": "tsv", "function": "get_column", "col_name": "name", "count": len(col)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == len(col)
    assert json.dumps(loaded[0]) is not None


def test_get_row_returns_list(tsv_sample, tmp_path):
    row = get_row(str(tsv_sample), 0)
    assert isinstance(row, list)
    assert len(row) > 0
    assert row[1] == "Alice"

    record = {"format": "tsv", "function": "get_row", "row_index": 0, "col_count": len(row)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["col_count"] == len(row)
    assert json.dumps(loaded[0]) is not None


def test_validate_headers_returns_dict(tsv_sample, tmp_path):
    result = validate_headers(str(tsv_sample), ["id", "name", "score"])
    assert isinstance(result, dict)
    assert result.get("valid") is True
    assert result.get("missing") == []

    record = {"format": "tsv", "function": "validate_headers", "valid": result["valid"], "missing_count": len(result["missing"])}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_to_csv_returns_string(tsv_sample, tmp_path):
    csv_str = to_csv(str(tsv_sample))
    assert isinstance(csv_str, str)
    assert "Alice" in csv_str
    assert "," in csv_str  # CSV uses comma separator

    record = {"format": "tsv", "function": "to_csv", "length": len(csv_str), "has_alice": "Alice" in csv_str}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["has_alice"] is True
    assert json.dumps(loaded[0]) is not None


def test_deduplicate_rows_removes_duplicates(tsv_sample, tmp_path):
    # tsv_sample has 3 rows with row 2 and 3 identical
    deduped = deduplicate_rows(str(tsv_sample))
    assert isinstance(deduped, list)
    assert len(deduped) == 2  # duplicate removed

    record = {"format": "tsv", "function": "deduplicate_rows", "original_rows": 3, "deduped_rows": len(deduped)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["deduped_rows"] == 2
    assert loaded[0]["original_rows"] > loaded[0]["deduped_rows"]
    assert json.dumps(loaded[0]) is not None
