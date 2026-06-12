"""
test_ndjson_group_count_by_pipeline.py -- NDJSON group_by + count_by pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-84
Tests group_by returns dict, group_by key count=2, count_by returns dict,
count_by has expected keys, count_by values are ints.
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
)

_RECORDS = [
    {"dept": "eng", "name": "Alice", "score": 85},
    {"dept": "hr", "name": "Bob", "score": 72},
    {"dept": "eng", "name": "Carol", "score": 91},
    {"dept": "hr", "name": "Dave", "score": 68},
    {"dept": "eng", "name": "Eve", "score": 78},
]


def test_group_by_returns_dict(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = group_by(str(dest), "dept")
    assert isinstance(result, dict)


def test_group_by_key_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = group_by(str(dest), "dept")
    assert len(result) == 2


def test_count_by_returns_dict(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = count_by(str(dest), "dept")
    assert isinstance(result, dict)


def test_count_by_has_expected_keys(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = count_by(str(dest), "dept")
    assert "eng" in result
    assert "hr" in result


def test_count_by_values_are_ints(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = count_by(str(dest), "dept")
    assert result["eng"] == 3
    assert result["hr"] == 2
