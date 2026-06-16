"""
Dogfood pipeline: TSV remaining + NDJSON aggregate functions → NDJSON export.
Covers: column_count, count_rows (tsv), aggregate, average_value, count_by, append_record (ndjson)
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from tsv.tsv_parser import column_count, count_rows
from ndjson.ndjson_codec import aggregate, average_value, count_by, append_record, write_ndjson, load_ndjson

_TSV_DIR = _REPO / "samples" / "by-format" / "tsv"


def _tsv_file():
    for f in sorted(_TSV_DIR.glob("*.tsv")):
        if "invalid" not in f.name and "binary" not in f.name:
            return str(f)
    return str(next(iter(sorted(_TSV_DIR.glob("*.tsv")))))


def test_tsv_column_count_returns_int(tmp_path):
    path = _tsv_file()
    result = column_count(path)
    assert isinstance(result, int)
    assert result >= 1
    record = {"format": "tsv", "function": "column_count", "column_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["column_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_tsv_count_rows_returns_int(tmp_path):
    path = _tsv_file()
    result = count_rows(path)
    assert isinstance(result, int)
    assert result >= 1
    record = {"format": "tsv", "function": "count_rows", "row_count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["row_count"] >= 1
    assert json.dumps(loaded[0]) is not None


def test_ndjson_aggregate_sum_returns_numeric(tmp_path):
    data_path = tmp_path / "data.ndjson"
    write_ndjson([{"x": 1}, {"x": 2}, {"x": 3}], str(data_path))
    result = aggregate(str(data_path), "x", "sum")
    assert isinstance(result, (int, float))
    assert result == 6
    record = {"format": "ndjson", "function": "aggregate", "sum": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["sum"] == 6
    assert json.dumps(loaded[0]) is not None


def test_ndjson_average_value_returns_float(tmp_path):
    data_path = tmp_path / "data.ndjson"
    write_ndjson([{"v": 10}, {"v": 20}, {"v": 30}], str(data_path))
    result = average_value(str(data_path), "v")
    assert isinstance(result, (int, float))
    assert result == 20.0
    record = {"format": "ndjson", "function": "average_value", "avg": float(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["avg"] == 20.0
    assert json.dumps(loaded[0]) is not None


def test_ndjson_count_by_returns_dict(tmp_path):
    data_path = tmp_path / "data.ndjson"
    write_ndjson([{"cat": "a"}, {"cat": "b"}, {"cat": "a"}], str(data_path))
    result = count_by(str(data_path), "cat")
    assert isinstance(result, dict)
    assert result.get("a") == 2
    record = {"format": "ndjson", "function": "count_by", "a_count": result.get("a", 0)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["a_count"] == 2
    assert json.dumps(loaded[0]) is not None


def test_ndjson_append_record_works(tmp_path):
    data_path = tmp_path / "data.ndjson"
    write_ndjson([{"n": 1}], str(data_path))
    append_record(str(data_path), {"n": 2})
    loaded = load_ndjson(str(data_path))
    assert len(loaded) == 2
    record = {"format": "ndjson", "function": "append_record", "total_records": len(loaded)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded2 = load_ndjson(str(ndjson_out))
    assert loaded2[0]["total_records"] == 2
    assert json.dumps(loaded2[0]) is not None
