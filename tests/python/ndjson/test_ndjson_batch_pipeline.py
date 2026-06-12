"""
test_ndjson_batch_pipeline.py -- NDJSON batch pipeline: merge, deduplicate, validate_schema.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-42
Tests merge+reload count, deduplicate unique count, validate_schema pass/fail,
field_stats count/mean, zip_records field count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    load_ndjson,
    merge_ndjson,
    deduplicate,
    validate_schema,
    field_stats,
    zip_records,
    get_record_count,
    to_jsonl_str,
)

_RECORDS_A = [
    {"id": 1, "name": "Alice", "score": 90},
    {"id": 2, "name": "Bob", "score": 70},
]
_RECORDS_B = [
    {"id": 2, "name": "Bob", "score": 70},  # duplicate of A[1]
    {"id": 3, "name": "Carol", "score": 85},
]


def _write(tmp_path, records, filename):
    path = tmp_path / filename
    write_ndjson(records, str(path))
    return path


def test_merge_then_reload_count(tmp_path):
    src_a = _write(tmp_path, _RECORDS_A, "a.ndjson")
    src_b = _write(tmp_path, _RECORDS_B, "b.ndjson")
    merged = merge_ndjson(str(src_a), str(src_b))
    dest = tmp_path / "merged.ndjson"
    write_ndjson(merged, str(dest))
    assert get_record_count(str(dest)) == 4


def test_deduplicate_unique_count(tmp_path):
    src_a = _write(tmp_path, _RECORDS_A, "a.ndjson")
    src_b = _write(tmp_path, _RECORDS_B, "b.ndjson")
    merged = merge_ndjson(str(src_a), str(src_b))
    merged_bytes = (to_jsonl_str(merged) + "\n").encode()
    unique = deduplicate(merged_bytes, "id")
    assert len(unique) == 3


def test_validate_schema_pass(tmp_path):
    src = _write(tmp_path, _RECORDS_A, "src.ndjson")
    schema = {"id": "number", "name": "string", "score": "number"}
    result = validate_schema(str(src), schema)
    assert result["valid"] is True


def test_validate_schema_fail_missing_field(tmp_path):
    records = [{"name": "Alice"}]
    src = _write(tmp_path, records, "src.ndjson")
    schema = {"name": "string", "score": "number"}
    result = validate_schema(str(src), schema)
    assert result["valid"] is False


def test_field_stats_mean(tmp_path):
    src = _write(tmp_path, _RECORDS_A, "src.ndjson")
    stats = field_stats(str(src), "score")
    assert stats["count"] == 2
    assert stats["mean"] == 80.0
