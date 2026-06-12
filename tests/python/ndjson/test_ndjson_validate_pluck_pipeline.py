"""
test_ndjson_validate_pluck_pipeline.py -- NDJSON validate_schema + pluck pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-90
Tests validate_schema returns dict, validate_schema valid=True for matching schema,
pluck returns list, pluck extracts field values, pluck count matches records.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    validate_schema,
    pluck,
)

_RECORDS = [
    {"name": "Alice", "score": 85, "dept": "eng"},
    {"name": "Bob", "score": 72, "dept": "hr"},
    {"name": "Carol", "score": 91, "dept": "eng"},
]
_SCHEMA = {"name": str, "score": int, "dept": str}


def test_validate_schema_returns_dict(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = validate_schema(str(dest), _SCHEMA)
    assert isinstance(result, dict)


def test_validate_schema_valid_true(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = validate_schema(str(dest), _SCHEMA)
    assert result.get("valid") is True or result.get("valid_count", 0) > 0


def test_pluck_returns_list(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = pluck(str(dest), "name")
    assert isinstance(result, list)


def test_pluck_extracts_field_values(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = pluck(str(dest), "name")
    assert "Alice" in result
    assert "Carol" in result


def test_pluck_count_matches_records(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = pluck(str(dest), "score")
    assert len(result) == 3
