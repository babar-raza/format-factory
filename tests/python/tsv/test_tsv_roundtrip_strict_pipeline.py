"""
test_tsv_roundtrip_strict_pipeline.py -- TSV roundtrip + write_tsv_strict pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-79
Tests roundtrip creates file, roundtrip returns dict, write_tsv_strict creates
file, get_headers from roundtrip file, count_rows from roundtrip.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    roundtrip,
    write_tsv_strict,
    get_headers,
    count_rows,
)

_TSV_DATA = b"city\tpop\trank\nParis\t2161000\t1\nLondon\t8982000\t2\nBerlin\t3645000\t3\n"


def test_roundtrip_creates_file(tmp_path):
    dest = tmp_path / "out.tsv"
    roundtrip(_TSV_DATA, str(dest))
    assert dest.exists()


def test_roundtrip_returns_dict(tmp_path):
    dest = tmp_path / "out.tsv"
    result = roundtrip(_TSV_DATA, str(dest))
    assert isinstance(result, dict)
    assert "rows" in result


def test_write_tsv_strict_creates_file(tmp_path):
    dest = tmp_path / "strict.tsv"
    write_tsv_strict(
        [["a", "b"], ["c", "d"]],
        str(dest),
        headers=["col1", "col2"],
    )
    assert dest.exists()


def test_get_headers_from_roundtrip(tmp_path):
    dest = tmp_path / "out.tsv"
    roundtrip(_TSV_DATA, str(dest))
    headers = get_headers(str(dest))
    assert "city" in headers
    assert "pop" in headers


def test_count_rows_from_roundtrip(tmp_path):
    dest = tmp_path / "out.tsv"
    roundtrip(_TSV_DATA, str(dest))
    result = count_rows(str(dest))
    assert result == 3
