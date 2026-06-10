"""Tests for NDJSON exports added in mainstream-product-deepening-rnext3.

Functions tested: merge_ndjson, group_by, sum_field, rename_field.

Covers: normal operation, empty sources, boundary cases, invalid input.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    merge_ndjson,
    group_by,
    sum_field,
    rename_field,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _ndjson_bytes(*records) -> bytes:
    import json
    return b"\n".join(json.dumps(r).encode() for r in records) + b"\n"


# ---------------------------------------------------------------------------
# merge_ndjson
# ---------------------------------------------------------------------------

def test_merge_ndjson_combines_two_sources():
    a = _ndjson_bytes({"id": 1}, {"id": 2})
    b = _ndjson_bytes({"id": 3})
    result = merge_ndjson(a, b)
    assert len(result) == 3
    assert result[0] == {"id": 1}
    assert result[2] == {"id": 3}


def test_merge_ndjson_preserves_order():
    a = _ndjson_bytes({"x": "a"}, {"x": "b"})
    b = _ndjson_bytes({"x": "c"}, {"x": "d"})
    result = merge_ndjson(a, b)
    assert [r["x"] for r in result] == ["a", "b", "c", "d"]


def test_merge_ndjson_empty_first_source():
    a = b""
    b = _ndjson_bytes({"val": 1})
    result = merge_ndjson(a, b)
    assert result == [{"val": 1}]


def test_merge_ndjson_both_empty():
    result = merge_ndjson(b"", b"")
    assert result == []


def test_merge_ndjson_returns_list():
    result = merge_ndjson(b"", b"")
    assert isinstance(result, list)


# ---------------------------------------------------------------------------
# group_by
# ---------------------------------------------------------------------------

def test_group_by_basic():
    src = _ndjson_bytes(
        {"type": "A", "val": 1},
        {"type": "B", "val": 2},
        {"type": "A", "val": 3},
    )
    result = group_by(src, "type")
    assert set(result.keys()) == {"A", "B"}
    assert len(result["A"]) == 2
    assert len(result["B"]) == 1


def test_group_by_missing_key_goes_to_none():
    src = _ndjson_bytes({"type": "X"}, {"other": "y"})
    result = group_by(src, "type")
    assert "X" in result
    assert None in result


def test_group_by_empty_source():
    result = group_by(b"", "type")
    assert result == {}


def test_group_by_returns_dict():
    result = group_by(_ndjson_bytes({"k": "v"}), "k")
    assert isinstance(result, dict)


def test_group_by_single_group():
    src = _ndjson_bytes({"cat": "Z"}, {"cat": "Z"}, {"cat": "Z"})
    result = group_by(src, "cat")
    assert list(result.keys()) == ["Z"]
    assert len(result["Z"]) == 3


# ---------------------------------------------------------------------------
# sum_field
# ---------------------------------------------------------------------------

def test_sum_field_basic():
    src = _ndjson_bytes({"score": 10}, {"score": 20}, {"score": 30})
    assert sum_field(src, "score") == 60.0


def test_sum_field_skips_missing():
    src = _ndjson_bytes({"score": 5}, {"other": 99}, {"score": 15})
    assert sum_field(src, "score") == 20.0


def test_sum_field_skips_non_numeric():
    src = _ndjson_bytes({"score": "abc"}, {"score": 10})
    assert sum_field(src, "score") == 10.0


def test_sum_field_empty_source():
    assert sum_field(b"", "score") == 0.0


def test_sum_field_returns_float():
    src = _ndjson_bytes({"n": 1})
    result = sum_field(src, "n")
    assert isinstance(result, float)


# ---------------------------------------------------------------------------
# rename_field
# ---------------------------------------------------------------------------

def test_rename_field_basic():
    src = _ndjson_bytes({"old": 1}, {"old": 2})
    result = rename_field(src, "old", "new")
    assert result[0] == {"new": 1}
    assert result[1] == {"new": 2}


def test_rename_field_preserves_other_fields():
    src = _ndjson_bytes({"a": 1, "b": 2})
    result = rename_field(src, "a", "renamed_a")
    assert result[0] == {"renamed_a": 1, "b": 2}


def test_rename_field_no_change_if_field_absent():
    src = _ndjson_bytes({"x": 1})
    result = rename_field(src, "missing", "new")
    assert result[0] == {"x": 1}


def test_rename_field_empty_source():
    result = rename_field(b"", "a", "b")
    assert result == []


def test_rename_field_returns_list():
    src = _ndjson_bytes({"k": "v"})
    result = rename_field(src, "k", "key")
    assert isinstance(result, list)
