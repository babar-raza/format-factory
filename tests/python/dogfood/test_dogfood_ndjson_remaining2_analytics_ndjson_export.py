"""
Dogfood pipeline: NDJSON remaining 2 analytics → NDJSON export.
Covers: filter_records, get_field_names, get_record_count, group_by,
        distinct_values, deduplicate
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO / "src" / "python"))

from ndjson.ndjson_codec import (
    filter_records,
    get_field_names,
    get_record_count,
    group_by,
    distinct_values,
    deduplicate,
    write_ndjson,
    load_ndjson,
)


def _make_data(tmp_path):
    path = tmp_path / "data.ndjson"
    write_ndjson([{"a": 1, "b": "x"}, {"a": 2, "b": "y"}, {"a": 1, "b": "x"}], str(path))
    return str(path)


def test_ndjson_filter_records_returns_list(tmp_path):
    path = _make_data(tmp_path)
    result = filter_records(path, "a", 1)
    assert isinstance(result, list)
    assert len(result) == 2
    record = {"format": "ndjson", "function": "filter_records", "match_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["match_count"] == 2
    assert json.dumps(loaded[0]) is not None


def test_ndjson_get_field_names_returns_list(tmp_path):
    path = _make_data(tmp_path)
    result = get_field_names(path)
    assert isinstance(result, list)
    assert "a" in result and "b" in result
    record = {"format": "ndjson", "function": "get_field_names", "field_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["field_count"] == 2
    assert json.dumps(loaded[0]) is not None


def test_ndjson_get_record_count_returns_int(tmp_path):
    path = _make_data(tmp_path)
    result = get_record_count(path)
    assert isinstance(result, int)
    assert result == 3
    record = {"format": "ndjson", "function": "get_record_count", "count": result}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 3
    assert json.dumps(loaded[0]) is not None


def test_ndjson_group_by_returns_dict(tmp_path):
    path = _make_data(tmp_path)
    result = group_by(path, "b")
    assert isinstance(result, dict)
    assert "x" in result and "y" in result
    record = {"format": "ndjson", "function": "group_by", "group_count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["group_count"] == 2
    assert json.dumps(loaded[0]) is not None


def test_ndjson_distinct_values_returns_list(tmp_path):
    path = _make_data(tmp_path)
    result = distinct_values(path, "b")
    assert isinstance(result, list)
    assert len(result) == 2
    record = {"format": "ndjson", "function": "distinct_values", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 2
    assert json.dumps(loaded[0]) is not None


def test_ndjson_deduplicate_returns_list(tmp_path):
    path = _make_data(tmp_path)
    result = deduplicate(path, "b")
    assert isinstance(result, list)
    assert len(result) == 2
    record = {"format": "ndjson", "function": "deduplicate", "count": len(result)}
    ndjson_out = tmp_path / "out.ndjson"
    write_ndjson([record], str(ndjson_out))
    loaded = load_ndjson(str(ndjson_out))
    assert loaded[0]["count"] == 2
    assert json.dumps(loaded[0]) is not None
