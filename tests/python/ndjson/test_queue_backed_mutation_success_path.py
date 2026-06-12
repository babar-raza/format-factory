"""
test_queue_backed_mutation_success_path.py -- NDJSON queue-backed mutation success path.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-7
Tests the queue-backed mutation path (write then reload) to verify
mutation operations correctly persist to disk.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    load_ndjson,
    write_ndjson,
    append_record,
    to_jsonl_str,
    filter_records,
    deduplicate,
    roundtrip,
)


_BASE_RECORDS = [
    {"id": 1, "name": "alpha", "val": 10},
    {"id": 2, "name": "beta", "val": 20},
    {"id": 3, "name": "alpha", "val": 30},
]


def _make_src(tmp_path):
    data = (to_jsonl_str(_BASE_RECORDS) + "\n").encode()
    p = tmp_path / "base.ndjson"
    p.write_bytes(data)
    return p


def test_append_record_persists(tmp_path):
    src = _make_src(tmp_path)
    dest = tmp_path / "appended.ndjson"
    src.replace(dest)
    append_record(dest, {"id": 4, "name": "gamma", "val": 40})
    reloaded = load_ndjson(dest)
    assert len(reloaded) == 4
    assert reloaded[-1]["name"] == "gamma"


def test_write_then_filter_consistency(tmp_path):
    src = _make_src(tmp_path)
    records = load_ndjson(src)
    out = tmp_path / "out.ndjson"
    write_ndjson(records, out)
    filtered = filter_records(out, "name", "alpha")
    assert len(filtered) == 2


def test_deduplicate_by_name(tmp_path):
    src = _make_src(tmp_path)
    deduped = deduplicate(src, "name")
    names = [r["name"] for r in deduped]
    assert len(names) == len(set(names))


def test_roundtrip_preserves_records(tmp_path):
    src = _make_src(tmp_path)
    out = tmp_path / "rt.ndjson"
    result = roundtrip(src, out)
    assert len(result) == len(_BASE_RECORDS)
    assert out.exists()


def test_write_empty_list(tmp_path):
    out = tmp_path / "empty.ndjson"
    write_ndjson([], out)
    assert out.exists()
    reloaded = load_ndjson(out)
    assert reloaded == []
