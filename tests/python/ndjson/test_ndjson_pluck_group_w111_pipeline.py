"""
test_ndjson_pluck_group_w111_pipeline.py -- NDJSON pluck + group_by pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-111
Tests pluck returns list, pluck extracts names, group_by returns dict,
group_by has correct keys, group_by eng count=2.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    pluck,
    group_by,
)

_RECORDS = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "hr"},
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "mkt"},
]

_SOURCE = to_jsonl_str(_RECORDS).encode()


def test_pluck_returns_list():
    result = pluck(_SOURCE, "name")
    assert isinstance(result, list)


def test_pluck_extracts_names():
    result = pluck(_SOURCE, "name")
    assert result == ["Alice", "Bob", "Carol", "Dave"]


def test_group_by_returns_dict():
    result = group_by(_SOURCE, "dept")
    assert isinstance(result, dict)


def test_group_by_has_correct_keys():
    result = group_by(_SOURCE, "dept")
    assert "eng" in result
    assert "hr" in result


def test_group_by_eng_count():
    result = group_by(_SOURCE, "dept")
    assert len(result["eng"]) == 2
