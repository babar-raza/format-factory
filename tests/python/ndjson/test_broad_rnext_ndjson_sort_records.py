"""Tests for NDJSON sort_records capability (broad-rnext sprint).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT-BROAD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import sort_records, write_ndjson


def _make_ndjson(tmp_path: Path, records: list[dict]) -> Path:
    p = tmp_path / "data.ndjson"
    write_ndjson(records, p)
    return p


def test_sort_records_ascending(tmp_path):
    """sort_records sorts by key ascending by default."""
    p = _make_ndjson(tmp_path, [{"n": 3}, {"n": 1}, {"n": 2}])
    result = sort_records(p, "n")
    assert [r["n"] for r in result] == [1, 2, 3]


def test_sort_records_descending(tmp_path):
    """sort_records with reverse=True sorts descending."""
    p = _make_ndjson(tmp_path, [{"n": 3}, {"n": 1}, {"n": 2}])
    result = sort_records(p, "n", reverse=True)
    assert [r["n"] for r in result] == [3, 2, 1]


def test_sort_records_string_key(tmp_path):
    """sort_records sorts string values lexicographically."""
    p = _make_ndjson(tmp_path, [{"name": "Charlie"}, {"name": "Alice"}, {"name": "Bob"}])
    result = sort_records(p, "name")
    assert [r["name"] for r in result] == ["Alice", "Bob", "Charlie"]


def test_sort_records_missing_key_sorted_to_end(tmp_path):
    """Records missing the sort key are sorted to end."""
    p = _make_ndjson(tmp_path, [{"n": 2}, {"x": "other"}, {"n": 1}])
    result = sort_records(p, "n")
    assert result[0]["n"] == 1
    assert result[1]["n"] == 2
    assert "n" not in result[2]


def test_sort_records_preserves_all_fields(tmp_path):
    """sort_records preserves all fields in each record."""
    records = [{"id": 2, "val": "b"}, {"id": 1, "val": "a"}]
    p = _make_ndjson(tmp_path, records)
    result = sort_records(p, "id")
    assert result[0] == {"id": 1, "val": "a"}
    assert result[1] == {"id": 2, "val": "b"}


def test_sort_records_returns_list(tmp_path):
    """sort_records always returns a list."""
    p = _make_ndjson(tmp_path, [{"k": 1}])
    result = sort_records(p, "k")
    assert isinstance(result, list)


def test_sort_records_empty_source(tmp_path):
    """sort_records on empty NDJSON returns empty list."""
    p = _make_ndjson(tmp_path, [])
    result = sort_records(p, "n")
    assert result == []


def test_sort_records_from_bytes():
    """sort_records accepts raw bytes as source."""
    raw = b'{"n": 3}\n{"n": 1}\n{"n": 2}\n'
    result = sort_records(raw, "n")
    assert [r["n"] for r in result] == [1, 2, 3]


def test_sort_records_stable(tmp_path):
    """sort_records is stable — equal keys preserve original order."""
    records = [{"n": 1, "label": "first"}, {"n": 1, "label": "second"}, {"n": 1, "label": "third"}]
    p = _make_ndjson(tmp_path, records)
    result = sort_records(p, "n")
    assert [r["label"] for r in result] == ["first", "second", "third"]


def test_sort_records_many_records(tmp_path):
    """sort_records handles many records correctly."""
    records = [{"i": i} for i in range(50, 0, -1)]
    p = _make_ndjson(tmp_path, records)
    result = sort_records(p, "i")
    assert len(result) == 50
    assert [r["i"] for r in result] == list(range(1, 51))
