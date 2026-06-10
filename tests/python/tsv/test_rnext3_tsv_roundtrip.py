"""Tests for TSV roundtrip capability (gap: GAP-TSV-FOSS-ROUNDTRIP-001).

Sprint: FORMAT-FACTORY-BROAD-CAPABILITY-LAYER-HEALING-RNEXT3
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO_ROOT))

from src.python.tsv.tsv_parser import roundtrip, write_tsv, load_tsv


def test_roundtrip_preserves_row_count(tmp_path):
    """roundtrip preserves row count."""
    src = tmp_path / "src.tsv"
    write_tsv([["a", "1"], ["b", "2"], ["c", "3"]], src, headers=["name", "val"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert result["row_count"] == 3


def test_roundtrip_preserves_headers(tmp_path):
    """roundtrip preserves headers."""
    src = tmp_path / "src.tsv"
    write_tsv([["x", "10"]], src, headers=["col1", "col2"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert result["headers"] == ["col1", "col2"]


def test_roundtrip_preserves_row_values(tmp_path):
    """roundtrip preserves row values."""
    rows = [["Alice", "99"], ["Bob", "42"]]
    src = tmp_path / "src.tsv"
    write_tsv(rows, src, headers=["name", "score"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert result["rows"][0] == ["Alice", "99"]
    assert result["rows"][1] == ["Bob", "42"]


def test_roundtrip_creates_dest_file(tmp_path):
    """roundtrip creates the destination file."""
    src = tmp_path / "src.tsv"
    write_tsv([["v1", "v2"]], src, headers=["a", "b"])
    dest = tmp_path / "dest.tsv"
    assert not dest.exists()
    roundtrip(src, dest)
    assert dest.exists()


def test_roundtrip_from_bytes(tmp_path):
    """roundtrip accepts raw bytes as source."""
    raw = b"col1\tcol2\nfoo\t1\nbar\t2\n"
    dest = tmp_path / "dest.tsv"
    result = roundtrip(raw, dest)
    assert result["row_count"] == 2


def test_roundtrip_returns_model_dict(tmp_path):
    """roundtrip returns a valid TSV model dict."""
    src = tmp_path / "src.tsv"
    write_tsv([["data"]], src, headers=["col"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert "row_count" in result
    assert "headers" in result
    assert "rows" in result


def test_roundtrip_single_row(tmp_path):
    """roundtrip works with a single data row."""
    src = tmp_path / "src.tsv"
    write_tsv([["only_val"]], src, headers=["col"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert result["row_count"] >= 1


def test_roundtrip_many_rows(tmp_path):
    """roundtrip preserves many rows."""
    rows = [[f"r{i}", str(i)] for i in range(30)]
    src = tmp_path / "src.tsv"
    write_tsv(rows, src, headers=["name", "num"])
    dest = tmp_path / "dest.tsv"
    result = roundtrip(src, dest)
    assert result["row_count"] == 30
