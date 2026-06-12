"""
test_ndjson_schema_validation.py -- NDJSON schema validation tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-13
Tests validate_schema with type checks, missing fields, wrong types,
and valid records returning expected counts.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import validate_schema, to_jsonl_str

_RECORDS = [
    {"name": "Alice", "score": 90, "active": True},
    {"name": "Bob", "score": 75, "active": False},
    {"name": "Carol", "score": 85, "active": True},
]
_SRC = (to_jsonl_str(_RECORDS) + "\n").encode()


def test_valid_schema_returns_true():
    result = validate_schema(_SRC, {"name": str, "score": int, "active": bool})
    assert result["valid"] is True


def test_valid_schema_total_records():
    result = validate_schema(_SRC, {"name": str})
    assert result["total_records"] == 3
    assert result["valid_records"] == 3


def test_missing_field_detected():
    result = validate_schema(_SRC, {"name": str, "missing_field": str})
    assert result["valid"] is False
    # All 3 records missing "missing_field"
    assert len(result["errors"]) == 3


def test_wrong_type_detected():
    # score is int, not str
    result = validate_schema(_SRC, {"score": str})
    assert result["valid"] is False
    assert any(e["error"] == "wrong_type" for e in result["errors"])


def test_partial_valid_count():
    # Only first record would fail if we add a field missing in some records
    mixed_records = [
        {"name": "Alice", "extra": 1},
        {"name": "Bob"},
        {"name": "Carol"},
    ]
    src = (to_jsonl_str(mixed_records) + "\n").encode()
    result = validate_schema(src, {"extra": int})
    assert result["total_records"] == 3
    # 2 records missing "extra"
    assert result["valid_records"] == 1


def test_empty_schema_always_valid():
    result = validate_schema(_SRC, {})
    assert result["valid"] is True
    assert result["valid_records"] == 3
