"""Tests for NDJSON roundtrip capability (gap: GAP-NDJSON-FOSS-ROUNDTRIP-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT3
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import roundtrip, write_ndjson


def test_roundtrip_preserves_record_count(tmp_path):
    """roundtrip preserves the number of records."""
    src = tmp_path / "src.ndjson"
    write_ndjson([{"a": 1}, {"a": 2}, {"a": 3}], src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert len(result) == 3


def test_roundtrip_preserves_field_values(tmp_path):
    """roundtrip preserves field values in each record."""
    records = [{"name": "Alice", "score": 99}, {"name": "Bob", "score": 42}]
    src = tmp_path / "src.ndjson"
    write_ndjson(records, src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert result[0]["name"] == "Alice"
    assert result[0]["score"] == 99
    assert result[1]["name"] == "Bob"
    assert result[1]["score"] == 42


def test_roundtrip_creates_dest_file(tmp_path):
    """roundtrip creates the destination file."""
    src = tmp_path / "src.ndjson"
    write_ndjson([{"x": 1}], src)
    dest = tmp_path / "dest.ndjson"
    assert not dest.exists()
    roundtrip(src, dest)
    assert dest.exists()


def test_roundtrip_from_bytes(tmp_path):
    """roundtrip accepts raw bytes as source."""
    raw = b'{"k": "val1"}\n{"k": "val2"}\n'
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(raw, dest)
    assert len(result) == 2
    assert result[0]["k"] == "val1"
    assert result[1]["k"] == "val2"


def test_roundtrip_empty_records(tmp_path):
    """roundtrip works for empty NDJSON (no records)."""
    src = tmp_path / "empty.ndjson"
    write_ndjson([], src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert result == []


def test_roundtrip_multiple_types(tmp_path):
    """roundtrip preserves multiple field types (str, int, float, bool, list)."""
    record = {"s": "hello", "i": 42, "f": 3.14, "b": True, "lst": [1, 2, 3]}
    src = tmp_path / "src.ndjson"
    write_ndjson([record], src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert result[0]["s"] == "hello"
    assert result[0]["i"] == 42
    assert result[0]["b"] is True
    assert result[0]["lst"] == [1, 2, 3]


def test_roundtrip_returns_list(tmp_path):
    """roundtrip always returns a list."""
    src = tmp_path / "src.ndjson"
    write_ndjson([{"id": 1}], src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert isinstance(result, list)


def test_roundtrip_many_records(tmp_path):
    """roundtrip preserves many records correctly."""
    records = [{"i": i, "val": f"item_{i}"} for i in range(50)]
    src = tmp_path / "src.ndjson"
    write_ndjson(records, src)
    dest = tmp_path / "dest.ndjson"
    result = roundtrip(src, dest)
    assert len(result) == 50
    for i, rec in enumerate(result):
        assert rec["i"] == i
        assert rec["val"] == f"item_{i}"
