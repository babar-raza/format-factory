"""Tests for ndjson.ndjson_codec.rename_field() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import rename_field, to_jsonl_str

RECORDS = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]


def _src():
    return to_jsonl_str(RECORDS).encode()


def test_renames_field():
    result = rename_field(_src(), "name", "full_name")
    assert result[0]["full_name"] == "Alice"
    assert result[1]["full_name"] == "Bob"


def test_old_field_removed():
    result = rename_field(_src(), "name", "full_name")
    assert "name" not in result[0]


def test_other_fields_unchanged():
    result = rename_field(_src(), "name", "full_name")
    assert result[0]["age"] == 30


def test_missing_field_record_unchanged():
    src = to_jsonl_str([{"x": 1}, {"name": "A", "x": 2}]).encode()
    result = rename_field(src, "name", "label")
    assert result[0] == {"x": 1}
    assert result[1] == {"label": "A", "x": 2}


def test_returns_list():
    assert isinstance(rename_field(_src(), "name", "label"), list)
