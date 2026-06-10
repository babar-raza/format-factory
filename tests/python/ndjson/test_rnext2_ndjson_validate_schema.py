"""Tests for NDJSON validate_schema capability (gap: GAP-NDJSON-FOSS-VALIDATE_SCH-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT2
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import validate_schema


def test_validate_schema_all_valid(tmp_path):
    """validate_schema returns valid=True when all records match schema."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"name": "Alice", "age": 30}\n{"name": "Bob", "age": 25}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"name": str, "age": int})
    assert result["valid"] is True
    assert result["total_records"] == 2
    assert result["valid_records"] == 2
    assert result["errors"] == []


def test_validate_schema_missing_field(tmp_path):
    """validate_schema detects missing required fields."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"name": "Alice"}\n{"age": 25}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"name": str, "age": int})
    assert result["valid"] is False
    errors = result["errors"]
    missing = [e for e in errors if e["error"] == "missing_field"]
    assert len(missing) >= 1


def test_validate_schema_wrong_type(tmp_path):
    """validate_schema detects wrong field type."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"name": 42, "age": 30}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"name": str, "age": int})
    assert result["valid"] is False
    errors = result["errors"]
    wrong = [e for e in errors if e["error"] == "wrong_type"]
    assert len(wrong) >= 1


def test_validate_schema_accepts_string_type_names(tmp_path):
    """validate_schema accepts schema with string type names."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"x": "hello", "count": 5}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"x": "str", "count": "int"})
    assert result["valid"] is True


def test_validate_schema_empty_schema(tmp_path):
    """validate_schema with empty schema always passes."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"anything": 1}\n{"other": "val"}\n', encoding="utf-8")
    result = validate_schema(ndjson, {})
    assert result["valid"] is True
    assert result["total_records"] == 2


def test_validate_schema_empty_file(tmp_path):
    """validate_schema on empty NDJSON file returns valid with 0 records."""
    ndjson = tmp_path / "empty.ndjson"
    ndjson.write_text("", encoding="utf-8")
    result = validate_schema(ndjson, {"x": str})
    assert result["total_records"] == 0
    assert result["valid"] is True


def test_validate_schema_returns_error_count(tmp_path):
    """validate_schema error list contains one entry per violation."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"a": "x"}\n{"a": 99}\n{"a": "y"}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"a": str})
    assert result["total_records"] == 3
    assert result["valid_records"] == 2
    assert len(result["errors"]) == 1


def test_validate_schema_from_bytes():
    """validate_schema accepts raw bytes input."""
    raw = b'{"k": "v1"}\n{"k": "v2"}\n'
    result = validate_schema(raw, {"k": str})
    assert result["valid"] is True
    assert result["total_records"] == 2


def test_validate_schema_multiple_errors(tmp_path):
    """validate_schema collects errors from multiple records."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"x": 1}\n{"x": 2}\n{"x": 3}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"x": str})
    assert result["valid"] is False
    assert len(result["errors"]) == 3


def test_validate_schema_bool_field(tmp_path):
    """validate_schema handles bool type correctly."""
    ndjson = tmp_path / "data.ndjson"
    ndjson.write_text('{"active": true}\n{"active": false}\n', encoding="utf-8")
    result = validate_schema(ndjson, {"active": bool})
    assert result["valid"] is True
