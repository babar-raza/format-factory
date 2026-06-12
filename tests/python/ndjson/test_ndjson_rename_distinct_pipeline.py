"""
test_ndjson_rename_distinct_pipeline.py -- NDJSON rename_field + distinct_values pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-96
Tests rename_field returns list, renamed field accessible, distinct_values returns list,
distinct_values correct count, distinct_values has expected values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import write_ndjson, rename_field, distinct_values

_RECORDS = [
    {"name": "Alice", "dept": "eng", "score": 85},
    {"name": "Bob", "dept": "hr", "score": 72},
    {"name": "Carol", "dept": "eng", "score": 91},
    {"name": "Dave", "dept": "hr", "score": 68},
]


def test_rename_field_returns_list(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = rename_field(str(dest), "name", "employee")
    assert isinstance(result, list)


def test_renamed_field_accessible(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = rename_field(str(dest), "name", "employee")
    assert "employee" in result[0]
    assert "name" not in result[0]


def test_distinct_values_returns_list(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = distinct_values(str(dest), "dept")
    assert isinstance(result, list)


def test_distinct_values_correct_count(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = distinct_values(str(dest), "dept")
    assert len(result) == 2


def test_distinct_values_has_expected(tmp_path):
    dest = tmp_path / "data.ndjson"
    write_ndjson(_RECORDS, str(dest))
    result = distinct_values(str(dest), "dept")
    assert "eng" in result
    assert "hr" in result
