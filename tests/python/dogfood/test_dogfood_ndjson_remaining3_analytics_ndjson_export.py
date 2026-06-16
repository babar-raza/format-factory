"""
Dogfood pipeline: NDJSON remaining analytics → NDJSON export.
Covers: validate_schema, sort_records, min_value, max_value, sort_by, tail
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    validate_schema,
    sort_records,
    min_value,
    max_value,
    sort_by,
    tail,
    write_ndjson,
    load_ndjson,
)


def test_ndjson_validate_schema_returns_dict(tmp_path):
    records = [{"x": 1, "y": "a"}, {"x": 2, "y": "b"}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = validate_schema(str(data_file), {"x": int, "y": str})
    assert isinstance(result, dict)
    assert result["valid"] is True
    assert result["total_records"] == 2

    summary = {"format": "ndjson", "function": "validate_schema", "valid": result["valid"], "total": result["total_records"]}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["valid"] is True
    assert json.dumps(loaded[0]) is not None


def test_ndjson_sort_records_returns_list(tmp_path):
    records = [{"x": 3, "y": "c"}, {"x": 1, "y": "a"}, {"x": 2, "y": "b"}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = sort_records(str(data_file), "x")
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["x"] == 1

    summary = {"format": "ndjson", "function": "sort_records", "count": len(result)}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_min_value_returns_value(tmp_path):
    records = [{"x": 3}, {"x": 1}, {"x": 2}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = min_value(str(data_file), "x")
    assert result == 1

    summary = {"format": "ndjson", "function": "min_value", "min": result}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["min"] == 1
    assert json.dumps(loaded[0]) is not None


def test_ndjson_max_value_returns_value(tmp_path):
    records = [{"x": 3}, {"x": 1}, {"x": 2}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = max_value(str(data_file), "x")
    assert result == 3

    summary = {"format": "ndjson", "function": "max_value", "max": result}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["max"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_sort_by_returns_list(tmp_path):
    records = [{"x": 3, "y": "c"}, {"x": 1, "y": "a"}, {"x": 2, "y": "b"}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = sort_by(str(data_file), "x")
    assert isinstance(result, list)
    assert len(result) == 3
    assert result[0]["x"] == 1

    summary = {"format": "ndjson", "function": "sort_by", "count": len(result)}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_tail_returns_list(tmp_path):
    records = [{"x": 1}, {"x": 2}, {"x": 3}, {"x": 4}, {"x": 5}]
    data_file = tmp_path / "data.ndjson"
    write_ndjson(records, str(data_file))

    result = tail(str(data_file), 2)
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[-1]["x"] == 5

    summary = {"format": "ndjson", "function": "tail", "count": len(result)}
    out = tmp_path / "out.ndjson"
    write_ndjson([summary], str(out))
    loaded = load_ndjson(str(out))
    assert loaded[0]["count"] == 2
    assert json.dumps(loaded[0]) is not None
