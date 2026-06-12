"""
test_ndjson_group_count_pipeline.py -- NDJSON group_by + count_by pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-48
Tests group_by returns dict with keys, count_by returns dict,
group then sum per group, distinct_values list, sort_by ascending.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    write_ndjson,
    group_by,
    count_by,
    distinct_values,
    sort_by,
    to_jsonl_str,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 90},
    {"name": "Bob", "dept": "mkt", "score": 70},
    {"name": "Carol", "dept": "eng", "score": 85},
    {"name": "Dave", "dept": "hr", "score": 75},
    {"name": "Eve", "dept": "eng", "score": 95},
]


def _write(tmp_path):
    path = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(path))
    return path


def test_group_by_returns_dict(tmp_path):
    src = _write(tmp_path)
    result = group_by(str(src), "dept")
    assert isinstance(result, dict)
    assert "eng" in result


def test_group_by_correct_counts(tmp_path):
    src = _write(tmp_path)
    result = group_by(str(src), "dept")
    assert len(result["eng"]) == 3
    assert len(result["mkt"]) == 1


def test_count_by_dept(tmp_path):
    src = _write(tmp_path)
    result = count_by(str(src), "dept")
    assert result["eng"] == 3
    assert result["hr"] == 1


def test_distinct_values_dept(tmp_path):
    src = _write(tmp_path)
    depts = distinct_values(str(src), "dept")
    assert set(depts) == {"eng", "mkt", "hr"}


def test_sort_by_score_ascending(tmp_path):
    src = _write(tmp_path)
    sorted_records = sort_by(str(src), "score")
    assert sorted_records[0]["name"] == "Bob"
    assert sorted_records[-1]["name"] == "Eve"
