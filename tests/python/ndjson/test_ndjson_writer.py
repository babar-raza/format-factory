"""Roundtrip tests for ndjson_writer.py — TC-W4-002."""
from __future__ import annotations

import json
import pytest
from pathlib import Path
from ndjson.ndjson_writer import write_ndjson, write_ndjson_str, NdjsonWriteError
from ndjson import load_ndjson


def test_write_ndjson_str_basic():
    records = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
    out = write_ndjson_str(records)
    lines = [l for l in out.strip().split("\n") if l]
    assert json.loads(lines[0]) == {"name": "Alice", "age": 30}
    assert json.loads(lines[1]) == {"name": "Bob", "age": 25}


def test_write_ndjson_str_empty():
    assert write_ndjson_str([]) == ""


def test_write_ndjson_str_non_serializable_raises():
    with pytest.raises(NdjsonWriteError, match="not JSON-serializable"):
        write_ndjson_str([{"val": object()}])


def test_write_ndjson_roundtrip(tmp_path):
    records = [{"x": 1, "y": "hello"}, {"x": 2, "y": "world"}]
    path = tmp_path / "out.ndjson"
    write_ndjson(records, path)
    result = load_ndjson(str(path))
    # load_ndjson returns a list of records directly
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] == {"x": 1, "y": "hello"}
    assert result[1] == {"x": 2, "y": "world"}


def test_write_ndjson_unicode(tmp_path):
    records = [{"msg": "héllo wörld"}]
    path = tmp_path / "unicode.ndjson"
    write_ndjson(records, path)
    content = path.read_text(encoding="utf-8")
    assert "héllo wörld" in content
