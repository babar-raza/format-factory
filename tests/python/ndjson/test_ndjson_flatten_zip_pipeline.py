"""
test_ndjson_flatten_zip_pipeline.py -- NDJSON flatten + zip_records pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-51
Tests flatten_records produces flat keys, nested keys removed,
zip_records combines dicts, zip_records field count, flatten + zip count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    flatten_records,
    zip_records,
    write_ndjson,
    load_ndjson,
)

_NESTED = [
    {"name": "Alice", "scores": {"math": 90, "eng": 85}},
    {"name": "Bob", "scores": {"math": 70, "eng": 75}},
]
_NAMES = [{"name": "Alice"}, {"name": "Bob"}, {"name": "Carol"}]
_SCORES = [{"score": 90}, {"score": 70}, {"score": 85}]


def test_flatten_produces_flat_keys():
    flat = flatten_records(_NESTED)
    assert "scores_math" in flat[0]
    assert "scores_eng" in flat[0]


def test_flatten_removes_nested_dict():
    flat = flatten_records(_NESTED)
    assert "scores" not in flat[0]


def test_zip_records_combines_dicts():
    zipped = zip_records(_NAMES, _SCORES)
    assert "name" in zipped[0]
    assert "score" in zipped[0]


def test_zip_records_count():
    zipped = zip_records(_NAMES, _SCORES)
    assert len(zipped) == 3


def test_flatten_then_write_reload(tmp_path):
    flat = flatten_records(_NESTED)
    dest = tmp_path / "flat.ndjson"
    write_ndjson(flat, str(dest))
    loaded = load_ndjson(str(dest))
    assert len(loaded) == 2
    assert loaded[0]["scores_math"] == 90
