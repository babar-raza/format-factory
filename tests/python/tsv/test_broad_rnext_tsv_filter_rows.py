"""Tests for TSV filter_rows capability (broad-rnext sprint).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT-BROAD-001
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.tsv.tsv_parser import filter_rows, write_tsv


def _make_tsv(tmp_path: Path, headers: list[str], rows: list[list[str]]) -> Path:
    p = tmp_path / "data.tsv"
    write_tsv(rows, p, headers=headers)
    return p


def test_filter_rows_exact_match(tmp_path):
    """filter_rows returns rows where column == value (exact)."""
    p = _make_tsv(tmp_path, ["name", "city"], [["Alice", "NYC"], ["Bob", "LA"], ["Carol", "NYC"]])
    result = filter_rows(p, "city", "NYC")
    assert result["row_count"] == 2
    assert all(r[1] == "NYC" for r in result["rows"])


def test_filter_rows_no_match(tmp_path):
    """filter_rows returns empty rows when no match."""
    p = _make_tsv(tmp_path, ["name", "city"], [["Alice", "NYC"], ["Bob", "LA"]])
    result = filter_rows(p, "city", "Paris")
    assert result["row_count"] == 0
    assert result["rows"] == []


def test_filter_rows_unknown_column(tmp_path):
    """filter_rows returns empty rows when column not in headers."""
    p = _make_tsv(tmp_path, ["name", "city"], [["Alice", "NYC"]])
    result = filter_rows(p, "country", "US")
    assert result["row_count"] == 0
    assert result["rows"] == []


def test_filter_rows_substring_match(tmp_path):
    """filter_rows with exact=False does substring matching."""
    p = _make_tsv(tmp_path, ["name", "email"], [["alice@example.com", "a"], ["bob@test.org", "b"]])
    result = filter_rows(p, "name", "example", exact=False)
    assert result["row_count"] == 1
    assert result["rows"][0][0] == "alice@example.com"


def test_filter_rows_case_insensitive(tmp_path):
    """filter_rows with case_sensitive=False matches regardless of case."""
    p = _make_tsv(tmp_path, ["name", "role"], [["Alice", "Admin"], ["Bob", "admin"], ["Carol", "User"]])
    result = filter_rows(p, "role", "admin", case_sensitive=False)
    assert result["row_count"] == 2


def test_filter_rows_preserves_headers(tmp_path):
    """filter_rows result contains original headers."""
    p = _make_tsv(tmp_path, ["name", "score"], [["Alice", "99"], ["Bob", "42"]])
    result = filter_rows(p, "name", "Alice")
    assert result["headers"] == ["name", "score"]


def test_filter_rows_returns_model_dict(tmp_path):
    """filter_rows returns a model dict with expected keys."""
    p = _make_tsv(tmp_path, ["a", "b"], [["x", "y"]])
    result = filter_rows(p, "a", "x")
    for key in ("format", "path", "row_count", "headers", "rows"):
        assert key in result


def test_filter_rows_single_column(tmp_path):
    """filter_rows works on a single-column TSV."""
    p = _make_tsv(tmp_path, ["tag"], [["alpha"], ["beta"], ["alpha"]])
    result = filter_rows(p, "tag", "alpha")
    assert result["row_count"] == 2


def test_filter_rows_from_bytes():
    """filter_rows accepts raw bytes as source."""
    raw = b"name\tcity\nAlice\tNYC\nBob\tLA\n"
    result = filter_rows(raw, "city", "NYC")
    assert result["row_count"] == 1
    assert result["rows"][0][0] == "Alice"


def test_filter_rows_all_match(tmp_path):
    """filter_rows returns all rows when all match."""
    p = _make_tsv(tmp_path, ["status", "val"], [["active", "1"], ["active", "2"], ["active", "3"]])
    result = filter_rows(p, "status", "active")
    assert result["row_count"] == 3
