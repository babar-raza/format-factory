"""
test_ndjson_deduplicate_pipeline.py -- NDJSON deduplicate + validate_schema pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-37
Tests deduplicate removes dupes by key, count reduced, write+reload deduped,
validate_schema pass for valid records, validate_schema fail for invalid.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    deduplicate,
    load_ndjson,
    validate_schema,
    get_record_count,
)

_RECORDS_WITH_DUPES = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice Duplicate"},  # dupe by id
    {"id": 3, "name": "Carol"},
]


def _write_src(tmp_path):
    src = tmp_path / "dupes.ndjson"
    write_ndjson(_RECORDS_WITH_DUPES, str(src))
    return src


def test_deduplicate_removes_dupe(tmp_path):
    src = _write_src(tmp_path)
    deduped = deduplicate(str(src), "id")
    assert len(deduped) == 3  # id 1,2,3 — one dupe removed


def test_deduplicate_write_reload(tmp_path):
    src = _write_src(tmp_path)
    deduped = deduplicate(str(src), "id")
    dest = tmp_path / "deduped.ndjson"
    write_ndjson(deduped, str(dest))
    assert get_record_count(str(dest)) == 3


def test_deduplicate_keeps_first(tmp_path):
    src = _write_src(tmp_path)
    deduped = deduplicate(str(src), "id")
    names = [r["name"] for r in deduped if r["id"] == 1]
    assert names[0] == "Alice"  # first occurrence kept


def test_validate_schema_pass(tmp_path):
    records = [{"name": "Alice", "score": 90}, {"name": "Bob", "score": 70}]
    src = tmp_path / "valid.ndjson"
    write_ndjson(records, str(src))
    schema = {"name": str, "score": int}
    result = validate_schema(str(src), schema)
    assert result["valid"] is True


def test_validate_schema_fail(tmp_path):
    records = [{"name": "Alice"}]  # missing "score"
    src = tmp_path / "invalid.ndjson"
    write_ndjson(records, str(src))
    schema = {"name": str, "score": int}
    result = validate_schema(str(src), schema)
    assert result["valid"] is False
