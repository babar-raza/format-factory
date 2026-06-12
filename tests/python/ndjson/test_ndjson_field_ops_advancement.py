"""
test_ndjson_field_ops_advancement.py -- NDJSON field operations advancement.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-11
Tests field_stats, rename_field, average_value, write_csv with content verification.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.ndjson.ndjson_codec import (
    field_stats,
    rename_field,
    average_value,
    write_csv,
    to_jsonl_str,
)

_RECORDS = [
    {"name": "Alice", "score": 90, "dept": "eng"},
    {"name": "Bob", "score": 75, "dept": "mkt"},
    {"name": "Carol", "score": 85, "dept": "eng"},
    {"name": "Dave", "score": 60, "dept": "mkt"},
]
_SRC = (to_jsonl_str(_RECORDS) + "\n").encode()


def test_field_stats_count():
    stats = field_stats(_SRC, "score")
    assert stats["count"] == 4


def test_field_stats_min_max():
    stats = field_stats(_SRC, "score")
    assert stats["min"] == 60.0
    assert stats["max"] == 90.0


def test_field_stats_sum_and_mean():
    stats = field_stats(_SRC, "score")
    assert stats["sum"] == 310.0
    assert abs(stats["mean"] - 77.5) < 0.001


def test_rename_field_new_name_present():
    result = rename_field(_SRC, "name", "full_name")
    assert all("full_name" in r for r in result)
    assert all("name" not in r for r in result)


def test_rename_field_values_preserved():
    result = rename_field(_SRC, "name", "full_name")
    names = [r["full_name"] for r in result]
    assert "Alice" in names
    assert "Dave" in names


def test_average_value_correct():
    avg = average_value(_SRC, "score")
    assert abs(avg - 77.5) < 0.001


def test_write_csv_creates_file(tmp_path):
    dest = tmp_path / "output.csv"
    write_csv(_SRC, str(dest))
    assert dest.exists()
    content = dest.read_text(encoding="utf-8")
    assert "Alice" in content
    assert "score" in content.lower() or "90" in content


def test_write_csv_has_all_records(tmp_path):
    dest = tmp_path / "output.csv"
    write_csv(_SRC, str(dest))
    lines = dest.read_text(encoding="utf-8").strip().splitlines()
    # header + 4 data rows = 5 lines
    assert len(lines) == 5
