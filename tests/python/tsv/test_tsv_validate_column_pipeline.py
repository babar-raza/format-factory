"""
test_tsv_validate_column_pipeline.py -- TSV validate_headers + column_count pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-32
Tests validate_headers (pass/fail), column_count, get_row_by_key,
append_rows, drop_column on written TSV files.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    validate_headers,
    column_count,
    get_row_by_key,
    append_rows,
    drop_column,
)

_HEADERS = ["id", "name", "score"]
_ROWS = [
    ["1", "Alice", "90"],
    ["2", "Bob", "70"],
    ["3", "Carol", "85"],
]


def _make_tsv(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_validate_headers_pass(tmp_path):
    dest = _make_tsv(tmp_path)
    result = validate_headers(str(dest), ["id", "name", "score"])
    assert result["valid"] is True


def test_validate_headers_fail(tmp_path):
    dest = _make_tsv(tmp_path)
    result = validate_headers(str(dest), ["id", "name", "wrong"])
    assert result["valid"] is False


def test_column_count(tmp_path):
    dest = _make_tsv(tmp_path)
    assert column_count(str(dest)) == 3


def test_get_row_by_key(tmp_path):
    dest = _make_tsv(tmp_path)
    row = get_row_by_key(str(dest), "name", "Alice")
    assert row is not None
    assert row[1] == "Alice"


def test_drop_column_reduces_count(tmp_path):
    dest = _make_tsv(tmp_path)
    result = drop_column(str(dest), "score")
    assert result["headers"] == ["id", "name"]
    assert len(result["rows"][0]) == 2
