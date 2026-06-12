"""
test_ndjson_validate_schema_pipeline.py -- NDJSON validate schema pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-66
Tests validate_schema valid, validate_schema returns dict, validate_schema invalid,
validate_schema total_records, validate_schema errors list.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    validate_schema,
)

_VALID_RECORDS = [
    {"id": 1, "name": "Alice", "active": True},
    {"id": 2, "name": "Bob", "active": False},
    {"id": 3, "name": "Carol", "active": True},
]
_INVALID_RECORDS = [
    {"id": 1, "name": "Alice"},
    {"id": "bad", "name": "Bob", "active": True},
]

_VALID_SOURCE = to_jsonl_str(_VALID_RECORDS).encode()
_INVALID_SOURCE = to_jsonl_str(_INVALID_RECORDS).encode()


def test_validate_schema_valid():
    result = validate_schema(_VALID_SOURCE, {"id": int, "name": str, "active": bool})
    assert result["valid"] is True


def test_validate_schema_returns_dict():
    result = validate_schema(_VALID_SOURCE, {"id": int})
    assert isinstance(result, dict)
    assert "valid" in result


def test_validate_schema_invalid():
    result = validate_schema(_INVALID_SOURCE, {"id": int, "name": str, "active": bool})
    assert result["valid"] is False


def test_validate_schema_total_records():
    result = validate_schema(_VALID_SOURCE, {"id": int})
    assert result["total_records"] == 3


def test_validate_schema_errors_list():
    result = validate_schema(_INVALID_SOURCE, {"id": int, "name": str, "active": bool})
    assert isinstance(result["errors"], list)
    assert len(result["errors"]) > 0
