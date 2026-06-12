"""Tests for NDJSON exports added in mainstream-product-deepening-rnext5.

Functions tested: to_jsonl_str, pluck, min_value, max_value, deduplicate.

Covers: normal operation, empty sources, boundary cases.
"""
from __future__ import annotations

import sys
from pathlib import Path


_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    pluck,
    min_value,
    max_value,
    deduplicate,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ndjson_bytes(*records) -> bytes:
    import json
    return b"\n".join(json.dumps(r).encode() for r in records) + b"\n"


# ---------------------------------------------------------------------------
# to_jsonl_str
# ---------------------------------------------------------------------------

def test_to_jsonl_str_basic():
    records = [{"a": 1}, {"b": 2}]
    result = to_jsonl_str(records)
    assert '{"a": 1}' in result
    assert '{"b": 2}' in result


def test_to_jsonl_str_separated_by_newlines():
    records = [{"x": 1}, {"x": 2}]
    result = to_jsonl_str(records)
    lines = result.split("\n")
    assert len(lines) == 2


def test_to_jsonl_str_empty_list():
    assert to_jsonl_str([]) == ""


def test_to_jsonl_str_returns_string():
    result = to_jsonl_str([{"k": "v"}])
    assert isinstance(result, str)


def test_to_jsonl_str_single_record():
    result = to_jsonl_str([{"hello": "world"}])
    import json
    parsed = json.loads(result)
    assert parsed == {"hello": "world"}


# ---------------------------------------------------------------------------
# pluck
# ---------------------------------------------------------------------------

def test_pluck_basic():
    src = _ndjson_bytes({"name": "Alice"}, {"name": "Bob"})
    assert pluck(src, "name") == ["Alice", "Bob"]


def test_pluck_skips_missing_field():
    src = _ndjson_bytes({"name": "Alice"}, {"age": 30}, {"name": "Bob"})
    assert pluck(src, "name") == ["Alice", "Bob"]


def test_pluck_empty_source():
    assert pluck(b"", "name") == []


def test_pluck_returns_list():
    src = _ndjson_bytes({"k": 1})
    assert isinstance(pluck(src, "k"), list)


def test_pluck_numeric_values():
    src = _ndjson_bytes({"score": 10}, {"score": 20}, {"score": 30})
    assert pluck(src, "score") == [10, 20, 30]


# ---------------------------------------------------------------------------
# min_value
# ---------------------------------------------------------------------------

def test_min_value_basic():
    src = _ndjson_bytes({"n": 5}, {"n": 2}, {"n": 8})
    assert min_value(src, "n") == 2


def test_min_value_skips_missing():
    src = _ndjson_bytes({"n": 5}, {"other": 1}, {"n": 3})
    assert min_value(src, "n") == 3


def test_min_value_empty_source():
    assert min_value(b"", "n") is None


def test_min_value_no_matching_field():
    src = _ndjson_bytes({"x": 1}, {"y": 2})
    assert min_value(src, "z") is None


def test_min_value_strings():
    src = _ndjson_bytes({"s": "banana"}, {"s": "apple"}, {"s": "cherry"})
    assert min_value(src, "s") == "apple"


# ---------------------------------------------------------------------------
# max_value
# ---------------------------------------------------------------------------

def test_max_value_basic():
    src = _ndjson_bytes({"n": 5}, {"n": 2}, {"n": 8})
    assert max_value(src, "n") == 8


def test_max_value_skips_missing():
    src = _ndjson_bytes({"n": 5}, {"other": 99}, {"n": 3})
    assert max_value(src, "n") == 5


def test_max_value_empty_source():
    assert max_value(b"", "n") is None


def test_max_value_no_matching_field():
    src = _ndjson_bytes({"x": 1})
    assert max_value(src, "z") is None


def test_max_value_strings():
    src = _ndjson_bytes({"s": "banana"}, {"s": "apple"}, {"s": "cherry"})
    assert max_value(src, "s") == "cherry"


# ---------------------------------------------------------------------------
# deduplicate
# ---------------------------------------------------------------------------

def test_deduplicate_basic():
    src = _ndjson_bytes({"id": 1}, {"id": 2}, {"id": 1})
    result = deduplicate(src, "id")
    assert len(result) == 2
    assert result[0] == {"id": 1}
    assert result[1] == {"id": 2}


def test_deduplicate_keeps_first_occurrence():
    src = _ndjson_bytes({"id": 1, "v": "a"}, {"id": 1, "v": "b"})
    result = deduplicate(src, "id")
    assert result == [{"id": 1, "v": "a"}]


def test_deduplicate_empty_source():
    assert deduplicate(b"", "id") == []


def test_deduplicate_returns_list():
    src = _ndjson_bytes({"k": "v"})
    assert isinstance(deduplicate(src, "k"), list)


def test_deduplicate_no_duplicates():
    src = _ndjson_bytes({"id": 1}, {"id": 2}, {"id": 3})
    result = deduplicate(src, "id")
    assert len(result) == 3
