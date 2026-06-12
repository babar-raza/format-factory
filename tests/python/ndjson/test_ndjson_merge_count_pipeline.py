"""
test_ndjson_merge_count_pipeline.py -- NDJSON merge + count pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-63
Tests merge_ndjson combines records, count_records after merge, count_records int,
merge preserves fields, count_records original.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    merge_ndjson,
    count_records,
)

_RECORDS_A = [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]
_RECORDS_B = [{"id": 3, "name": "Carol"}, {"id": 4, "name": "Dave"}, {"id": 5, "name": "Eve"}]

_SOURCE_A = to_jsonl_str(_RECORDS_A).encode()
_SOURCE_B = to_jsonl_str(_RECORDS_B).encode()


def test_merge_ndjson_combines_records():
    result = merge_ndjson(_SOURCE_A, _SOURCE_B)
    assert len(result) == 5


def test_count_records_after_merge():
    merged = merge_ndjson(_SOURCE_A, _SOURCE_B)
    src = to_jsonl_str(merged).encode()
    count = count_records(src)
    assert count == 5


def test_count_records_int():
    count = count_records(_SOURCE_A)
    assert isinstance(count, int)
    assert count == 2


def test_merge_preserves_fields():
    result = merge_ndjson(_SOURCE_A, _SOURCE_B)
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Carol" in names


def test_count_records_original():
    count = count_records(_SOURCE_B)
    assert count == 3
