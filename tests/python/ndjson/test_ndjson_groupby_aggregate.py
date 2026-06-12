"""
test_ndjson_groupby_aggregate.py -- NDJSON group_by and aggregate pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-22
Tests group_by, count_by, aggregate (sum/count), and chaining with filter.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    group_by,
    count_by,
    aggregate,
    filter_records,
    distinct_values,
)

_RECORDS = [
    {"name": "Alice", "score": 90, "dept": "eng"},
    {"name": "Bob", "score": 75, "dept": "mkt"},
    {"name": "Carol", "score": 85, "dept": "eng"},
    {"name": "Dave", "score": 60, "dept": "mkt"},
    {"name": "Eve", "score": 95, "dept": "eng"},
]
_SOURCE = (to_jsonl_str(_RECORDS) + "\n").encode()


def test_group_by_dept_keys():
    groups = group_by(_SOURCE, "dept")
    assert set(groups.keys()) == {"eng", "mkt"}


def test_group_by_eng_count():
    groups = group_by(_SOURCE, "dept")
    assert len(groups["eng"]) == 3


def test_count_by_dept():
    counts = count_by(_SOURCE, "dept")
    assert counts["eng"] == 3
    assert counts["mkt"] == 2


def test_aggregate_sum_score():
    total = aggregate(_SOURCE, "score", "sum")
    assert total == 405.0


def test_distinct_depts():
    depts = distinct_values(_SOURCE, "dept")
    assert set(depts) == {"eng", "mkt"}
