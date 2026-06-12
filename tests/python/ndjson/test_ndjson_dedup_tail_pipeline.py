"""
test_ndjson_dedup_tail_pipeline.py -- NDJSON deduplicate + tail pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-108
Tests deduplicate returns list, removes dup by dept count=3, tail returns list,
tail last=Dave, tail count=2.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    deduplicate,
    tail,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "hr"},
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "hr"},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_deduplicate_returns_list():
    result = deduplicate(_SOURCE, "dept")
    assert isinstance(result, list)


def test_deduplicate_removes_dups():
    result = deduplicate(_SOURCE, "dept")
    assert len(result) == 2


def test_tail_returns_list():
    result = tail(_SOURCE, 2)
    assert isinstance(result, list)


def test_tail_last_record():
    result = tail(_SOURCE, 2)
    assert result[-1]["name"] == "Dave"


def test_tail_count():
    result = tail(_SOURCE, 2)
    assert len(result) == 2
