"""
test_ndjson_write_reload_pipeline.py -- NDJSON write + reload pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-69
Tests write_ndjson creates file, load_ndjson returns list, roundtrip count,
roundtrip preserves data, write then count_records.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    roundtrip,
    count_records,
)

_RECORDS = [
    {"id": 1, "name": "Alice", "score": 90},
    {"id": 2, "name": "Bob", "score": 80},
    {"id": 3, "name": "Carol", "score": 70},
]


def test_write_ndjson_creates_file(tmp_path):
    dest = tmp_path / "out.ndjson"
    write_ndjson(_RECORDS, str(dest))
    assert dest.exists()


def test_load_ndjson_returns_list(tmp_path):
    dest = tmp_path / "out.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = load_ndjson(str(dest))
    assert isinstance(result, list)
    assert len(result) == 3


def test_roundtrip_count(tmp_path):
    dest = tmp_path / "rt.ndjson"
    from src.python.ndjson.ndjson_codec import to_jsonl_str
    src = to_jsonl_str(_RECORDS).encode()
    result = roundtrip(src, str(dest))
    assert len(result) == 3


def test_roundtrip_preserves_data(tmp_path):
    dest = tmp_path / "rt.ndjson"
    from src.python.ndjson.ndjson_codec import to_jsonl_str
    src = to_jsonl_str(_RECORDS).encode()
    result = roundtrip(src, str(dest))
    names = [r["name"] for r in result]
    assert "Alice" in names


def test_write_then_count_records(tmp_path):
    dest = tmp_path / "count.ndjson"
    write_ndjson(_RECORDS, str(dest))
    count = count_records(str(dest))
    assert count == 3
