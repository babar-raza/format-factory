"""
test_ndjson_flatten_pipeline.py -- NDJSON flatten_records pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-28
Tests flatten_records: nested dict expansion, key naming, count preserved,
write flattened then reload, field names after flatten.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    flatten_records,
    write_ndjson,
    load_ndjson,
    get_field_names,
)

_NESTED = [
    {"name": "Alice", "scores": {"math": 90, "eng": 85}},
    {"name": "Bob", "scores": {"math": 75, "eng": 80}},
]


def test_flatten_expands_nested_keys():
    flat = flatten_records(_NESTED)
    assert "scores_math" in flat[0]
    assert "scores_eng" in flat[0]


def test_flatten_removes_nested_dict():
    flat = flatten_records(_NESTED)
    assert "scores" not in flat[0]


def test_flatten_preserves_record_count():
    flat = flatten_records(_NESTED)
    assert len(flat) == 2


def test_flatten_write_reload(tmp_path):
    flat = flatten_records(_NESTED)
    dest = tmp_path / "flat.ndjson"
    write_ndjson(flat, str(dest))
    reloaded = load_ndjson(str(dest))
    assert len(reloaded) == 2
    assert "scores_math" in reloaded[0]


def test_flatten_field_names(tmp_path):
    flat = flatten_records(_NESTED)
    dest = tmp_path / "flat.ndjson"
    write_ndjson(flat, str(dest))
    fields = get_field_names(str(dest))
    assert "name" in fields
    assert "scores_math" in fields
