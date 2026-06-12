"""
test_dogfood_tsv_ndjson_pipeline.py -- TSV→NDJSON cross-format pipeline dogfood.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-17
Tests converting TSV data to NDJSON records, then applying NDJSON operations.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "src" / "python"))

from src.python.tsv.tsv_parser import load_tsv, get_headers
from src.python.ndjson.ndjson_codec import (
    to_jsonl_str,
    load_ndjson,
    write_ndjson,
    filter_records,
    get_field_names,
)

_TSV_BYTES = b"name\tscore\tdept\nAlice\t90\teng\nBob\t75\tmkt\nCarol\t85\teng\n"


def _tsv_to_ndjson_records(tsv_data: dict) -> list[dict]:
    """Convert TSV neutral model to NDJSON records."""
    headers = tsv_data["headers"]
    return [dict(zip(headers, row)) for row in tsv_data["rows"]]


def test_tsv_to_ndjson_record_count():
    data = load_tsv(_TSV_BYTES)
    records = _tsv_to_ndjson_records(data)
    assert len(records) == 3


def test_tsv_to_ndjson_field_names():
    data = load_tsv(_TSV_BYTES)
    records = _tsv_to_ndjson_records(data)
    src = (to_jsonl_str(records) + "\n").encode()
    fields = get_field_names(src)
    assert "name" in fields
    assert "score" in fields
    assert "dept" in fields


def test_tsv_to_ndjson_filter_pipeline():
    data = load_tsv(_TSV_BYTES)
    records = _tsv_to_ndjson_records(data)
    src = (to_jsonl_str(records) + "\n").encode()
    eng_records = filter_records(src, "dept", "eng")
    assert len(eng_records) == 2
    names = [r["name"] for r in eng_records]
    assert "Alice" in names
    assert "Carol" in names


def test_tsv_to_ndjson_write_reload_pipeline(tmp_path):
    data = load_tsv(_TSV_BYTES)
    records = _tsv_to_ndjson_records(data)
    dest = tmp_path / "converted.ndjson"
    write_ndjson(records, str(dest))
    reloaded = load_ndjson(str(dest))
    assert len(reloaded) == 3
    assert reloaded[0]["name"] == "Alice"
