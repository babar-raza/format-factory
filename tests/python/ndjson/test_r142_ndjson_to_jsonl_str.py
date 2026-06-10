"""Tests for ndjson_codec.to_jsonl_str() — Sprint 7, R142."""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import to_jsonl_str


def test_basic_output():
    records = [{"a": 1}, {"b": 2}]
    result = to_jsonl_str(records)
    lines = result.split("\n")
    assert len(lines) == 2
    assert json.loads(lines[0]) == {"a": 1}
    assert json.loads(lines[1]) == {"b": 2}


def test_empty_list():
    result = to_jsonl_str([])
    assert result == ""


def test_single_record():
    result = to_jsonl_str([{"x": 42}])
    assert json.loads(result) == {"x": 42}


def test_returns_string():
    result = to_jsonl_str([{"a": 1}])
    assert isinstance(result, str)


def test_roundtrip():
    records = [{"id": i} for i in range(5)]
    s = to_jsonl_str(records)
    reloaded = [json.loads(line) for line in s.split("\n") if line]
    assert reloaded == records


def test_non_ascii_preserved():
    records = [{"name": "héllo"}]
    result = to_jsonl_str(records)
    assert "héllo" in result
