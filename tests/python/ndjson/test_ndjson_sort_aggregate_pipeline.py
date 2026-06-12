"""
test_ndjson_sort_aggregate_pipeline.py -- NDJSON sort_by + aggregate pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-102
Tests sort_by returns list, first record has lowest score, aggregate sum=310,
aggregate max=90, aggregate count=4.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    sort_by,
    aggregate,
)

_RECORDS = [
    {"name": "Alice", "score": 90},
    {"name": "Bob", "score": 70},
    {"name": "Carol", "score": 85},
    {"name": "Dave", "score": 65},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_sort_by_returns_list():
    result = sort_by(_SOURCE, "score")
    assert isinstance(result, list)


def test_sort_by_ascending_first():
    result = sort_by(_SOURCE, "score")
    assert result[0]["name"] == "Dave"


def test_aggregate_sum_correct():
    total = aggregate(_SOURCE, "score", "sum")
    assert total == 310


def test_aggregate_max_correct():
    maximum = aggregate(_SOURCE, "score", "max")
    assert maximum == 90


def test_aggregate_count_correct():
    count = aggregate(_SOURCE, "score", "count")
    assert count == 4
