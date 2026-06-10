"""Tests for NDJSON write_csv and field_stats.

Sprint: product-progress-rnext
"""
from __future__ import annotations

import csv
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.ndjson.ndjson_codec import write_csv, field_stats, to_jsonl_str

RECORDS = [
    {"name": "Alice", "score": 90, "active": True},
    {"name": "Bob", "score": 75, "active": False},
    {"name": "Carol", "score": 85, "active": True},
]


def _src():
    return to_jsonl_str(RECORDS).encode()


def test_write_csv_creates_file(tmp_path):
    """write_csv creates a CSV file at dest."""
    dest = tmp_path / "out.csv"
    write_csv(_src(), dest)
    assert dest.exists()


def test_write_csv_file_nonempty(tmp_path):
    """write_csv writes non-empty content."""
    dest = tmp_path / "out.csv"
    write_csv(_src(), dest)
    assert dest.stat().st_size > 0


def test_write_csv_contains_headers(tmp_path):
    """write_csv includes header row."""
    dest = tmp_path / "out.csv"
    write_csv(_src(), dest)
    content = dest.read_text(encoding="utf-8")
    assert "name" in content
    assert "score" in content


def test_write_csv_contains_data(tmp_path):
    """write_csv includes record values."""
    dest = tmp_path / "out.csv"
    write_csv(_src(), dest)
    content = dest.read_text(encoding="utf-8")
    assert "Alice" in content
    assert "90" in content


def test_write_csv_parseable(tmp_path):
    """write_csv output is valid CSV parseable by stdlib csv module."""
    dest = tmp_path / "out.csv"
    write_csv(_src(), dest)
    with open(dest, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    assert len(rows) == 3
    names = [r["name"] for r in rows]
    assert "Alice" in names
    assert "Bob" in names


def test_field_stats_count():
    """field_stats returns correct count of numeric values."""
    result = field_stats(_src(), "score")
    assert result["count"] == 3


def test_field_stats_min_max():
    """field_stats returns correct min and max."""
    result = field_stats(_src(), "score")
    assert result["min"] == 75.0
    assert result["max"] == 90.0


def test_field_stats_sum():
    """field_stats returns correct sum."""
    result = field_stats(_src(), "score")
    assert result["sum"] == 250.0


def test_field_stats_mean():
    """field_stats returns correct mean."""
    result = field_stats(_src(), "score")
    assert abs(result["mean"] - 250.0 / 3) < 1e-9


def test_field_stats_missing_field():
    """field_stats handles missing field with missing count."""
    result = field_stats(_src(), "nonexistent")
    assert result["count"] == 0
    assert result["missing"] == 3
    assert result["min"] is None


def test_field_stats_non_numeric_field():
    """field_stats counts non-numeric values as missing."""
    result = field_stats(_src(), "name")
    assert result["count"] == 0
    assert result["missing"] == 3
