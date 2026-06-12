"""
test_ndjson_deduplicate_head_pipeline.py -- NDJSON deduplicate + head pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-60
Tests deduplicate removes dupe, head count, head returns list,
deduplicate then head, deduplicate preserves order.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    deduplicate,
    head,
)

_RECORDS = [
    {"id": 1, "name": "Alice"},
    {"id": 2, "name": "Bob"},
    {"id": 1, "name": "Alice"},
    {"id": 3, "name": "Carol"},
    {"id": 2, "name": "Bob"},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_deduplicate_removes_dupe():
    result = deduplicate(_SOURCE, "id")
    assert len(result) == 3


def test_head_count():
    result = head(_SOURCE, 2)
    assert len(result) == 2


def test_head_returns_list():
    result = head(_SOURCE, 3)
    assert isinstance(result, list)


def test_deduplicate_then_head():
    unique = deduplicate(_SOURCE, "id")
    src2 = to_jsonl_str(unique).encode()
    top2 = head(src2, 2)
    assert len(top2) == 2


def test_deduplicate_preserves_first():
    result = deduplicate(_SOURCE, "id")
    ids = [r["id"] for r in result]
    assert ids[0] == 1
