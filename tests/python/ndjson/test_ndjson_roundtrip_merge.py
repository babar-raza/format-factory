"""
test_ndjson_roundtrip_merge.py -- NDJSON roundtrip and merge deepening.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-16
Tests roundtrip (write+reload), merge_ndjson content, and related operations
with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    roundtrip,
    merge_ndjson,
    to_jsonl_str,
    load_ndjson,
    write_ndjson,
    get_record_count,
)

_RECORDS_A = [
    {"name": "Alice", "dept": "eng"},
    {"name": "Bob", "dept": "mkt"},
]
_RECORDS_B = [
    {"name": "Carol", "dept": "eng"},
    {"name": "Dave", "dept": "hr"},
]
_SRC_A = (to_jsonl_str(_RECORDS_A) + "\n").encode()
_SRC_B = (to_jsonl_str(_RECORDS_B) + "\n").encode()


def test_roundtrip_preserves_count(tmp_path):
    src = tmp_path / "input.ndjson"
    src.write_bytes(_SRC_A)
    dest = tmp_path / "output.ndjson"
    result = roundtrip(str(src), str(dest))
    assert len(result) == 2


def test_roundtrip_preserves_field_values(tmp_path):
    src = tmp_path / "input.ndjson"
    src.write_bytes(_SRC_A)
    dest = tmp_path / "output.ndjson"
    result = roundtrip(str(src), str(dest))
    names = [r["name"] for r in result]
    assert "Alice" in names
    assert "Bob" in names


def test_roundtrip_dest_file_exists(tmp_path):
    src = tmp_path / "input.ndjson"
    src.write_bytes(_SRC_A)
    dest = tmp_path / "output.ndjson"
    roundtrip(str(src), str(dest))
    assert dest.exists()


def test_roundtrip_dest_loadable(tmp_path):
    src = tmp_path / "input.ndjson"
    src.write_bytes(_SRC_A)
    dest = tmp_path / "output.ndjson"
    roundtrip(str(src), str(dest))
    reloaded = load_ndjson(str(dest))
    assert len(reloaded) == 2


def test_merge_ndjson_count():
    merged = merge_ndjson(_SRC_A, _SRC_B)
    assert len(merged) == 4


def test_merge_ndjson_contains_all_names():
    merged = merge_ndjson(_SRC_A, _SRC_B)
    names = [r["name"] for r in merged]
    assert "Alice" in names
    assert "Bob" in names
    assert "Carol" in names
    assert "Dave" in names


def test_write_then_count(tmp_path):
    dest = tmp_path / "out.ndjson"
    write_ndjson(_RECORDS_A, str(dest))
    count = get_record_count(str(dest))
    assert count == 2


def test_write_ndjson_reload_values(tmp_path):
    dest = tmp_path / "out.ndjson"
    write_ndjson(_RECORDS_A, str(dest))
    reloaded = load_ndjson(str(dest))
    assert reloaded[0]["name"] == "Alice"
    assert reloaded[1]["dept"] == "mkt"
