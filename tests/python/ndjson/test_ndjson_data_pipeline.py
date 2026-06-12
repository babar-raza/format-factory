"""
test_ndjson_data_pipeline.py -- NDJSON product deepening: data pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-6
Tests NDJSON transform/analytics functions with real data validation.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    load_ndjson,
    write_ndjson,
    export_to_csv,
    filter_records,
    get_field_names,
    sort_records,
    group_by,
    head,
    tail,
    min_value,
    max_value,
    pick,
    distinct_values,
    aggregate,
    to_jsonl_str,
    count_by,
    pluck,
    sum_field,
)


_RECORDS = [
    {"name": "Alice", "score": 90, "dept": "eng"},
    {"name": "Bob", "score": 75, "dept": "mkt"},
    {"name": "Carol", "score": 85, "dept": "eng"},
    {"name": "Dave", "score": 75, "dept": "mkt"},
]


def _make_src(tmp_path, records=None):
    if records is None:
        records = _RECORDS
    data = to_jsonl_str(records).encode()
    p = tmp_path / "data.ndjson"
    p.write_bytes(data)
    return p


def test_load_and_count(tmp_path):
    src = _make_src(tmp_path)
    records = load_ndjson(src)
    assert len(records) == 4


def test_get_field_names(tmp_path):
    src = _make_src(tmp_path)
    fields = get_field_names(src)
    assert "name" in fields
    assert "score" in fields
    assert "dept" in fields


def test_filter_records(tmp_path):
    src = _make_src(tmp_path)
    results = filter_records(src, "dept", "eng")
    assert len(results) == 2
    assert all(r["dept"] == "eng" for r in results)


def test_sort_records_ascending(tmp_path):
    src = _make_src(tmp_path)
    sorted_recs = sort_records(src, "score")
    scores = [r["score"] for r in sorted_recs]
    assert scores == sorted(scores)


def test_group_by_dept(tmp_path):
    src = _make_src(tmp_path)
    grouped = group_by(src, "dept")
    assert "eng" in grouped
    assert "mkt" in grouped
    assert len(grouped["eng"]) == 2


def test_head(tmp_path):
    src = _make_src(tmp_path)
    first = head(src, 2)
    assert len(first) == 2
    assert first[0]["name"] == "Alice"


def test_tail(tmp_path):
    src = _make_src(tmp_path)
    last = tail(src, 2)
    assert len(last) == 2
    assert last[-1]["name"] == "Dave"


def test_min_max_value(tmp_path):
    src = _make_src(tmp_path)
    assert min_value(src, "score") == 75
    assert max_value(src, "score") == 90


def test_pick_fields(tmp_path):
    src = _make_src(tmp_path)
    picked = pick(src, ["name", "score"])
    assert all(set(r.keys()) == {"name", "score"} for r in picked)


def test_distinct_values(tmp_path):
    src = _make_src(tmp_path)
    depts = distinct_values(src, "dept")
    assert set(depts) == {"eng", "mkt"}


def test_aggregate_sum(tmp_path):
    src = _make_src(tmp_path)
    total = aggregate(src, "score", "sum")
    assert total == 325


def test_count_by(tmp_path):
    src = _make_src(tmp_path)
    counts = count_by(src, "dept")
    assert counts["eng"] == 2
    assert counts["mkt"] == 2


def test_pluck(tmp_path):
    src = _make_src(tmp_path)
    names = pluck(src, "name")
    assert names == ["Alice", "Bob", "Carol", "Dave"]


def test_sum_field(tmp_path):
    src = _make_src(tmp_path)
    total = sum_field(src, "score")
    assert total == 325.0


def test_export_to_csv_has_header(tmp_path):
    src = _make_src(tmp_path)
    csv_str = export_to_csv(src)
    lines = [l for l in csv_str.splitlines() if l.strip()]
    assert len(lines) >= 2
    header = lines[0]
    assert "name" in header or "score" in header


def test_write_and_reload(tmp_path):
    src = _make_src(tmp_path)
    records = load_ndjson(src)
    out = tmp_path / "out.ndjson"
    write_ndjson(records, out)
    reloaded = load_ndjson(out)
    assert reloaded == records
