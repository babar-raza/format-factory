"""
test_tsv_write_reload_roundtrip.py -- TSV write and reload roundtrip tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-20
Tests that write_tsv and write_tsv_strict produce TSV files that can be
reloaded with correct headers, rows, and column values.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    write_tsv_strict,
    load_tsv,
    get_headers,
    count_rows,
    get_column,
    get_row,
)

_HEADERS = ["name", "score", "dept"]
_ROWS = [
    ["Alice", "90", "eng"],
    ["Bob", "75", "mkt"],
    ["Carol", "85", "eng"],
]


def test_write_tsv_headers_persist(tmp_path):
    dest = tmp_path / "out.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    headers = get_headers(str(dest))
    assert headers == _HEADERS


def test_write_tsv_row_count_correct(tmp_path):
    dest = tmp_path / "out.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    assert count_rows(str(dest)) == 3


def test_write_tsv_column_values_correct(tmp_path):
    dest = tmp_path / "out.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    col = get_column(str(dest), "name")
    assert col == ["Alice", "Bob", "Carol"]


def test_write_tsv_strict_row_data_correct(tmp_path):
    dest = tmp_path / "strict.tsv"
    write_tsv_strict(_ROWS, str(dest), headers=_HEADERS)
    result = load_tsv(str(dest))
    assert result["rows"][0] == ["Alice", "90", "eng"]
    assert result["rows"][2] == ["Carol", "85", "eng"]


def test_write_tsv_reload_preserves_second_row(tmp_path):
    dest = tmp_path / "reload.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    row = get_row(str(dest), 1)
    assert row == ["Bob", "75", "mkt"]
