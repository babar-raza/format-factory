"""
test_tsv_to_csv_roundtrip.py -- TSV to_csv + roundtrip pipeline tests.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-37
Tests to_csv produces comma-separated string, roundtrip produces dict,
roundtrip preserves row count, append_rows adds rows, get_column_values extracts column.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    write_tsv,
    to_csv,
    roundtrip,
    append_rows,
    get_column_values,
)

_HEADERS = ["name", "score"]
_ROWS = [
    ["Alice", "90"],
    ["Bob", "70"],
    ["Carol", "85"],
]


def _make_tsv(tmp_path):
    dest = tmp_path / "data.tsv"
    write_tsv(_ROWS, str(dest), headers=_HEADERS)
    return dest


def test_to_csv_is_string(tmp_path):
    dest = _make_tsv(tmp_path)
    csv_str = to_csv(str(dest))
    assert isinstance(csv_str, str)
    assert "Alice" in csv_str


def test_to_csv_has_commas(tmp_path):
    dest = _make_tsv(tmp_path)
    csv_str = to_csv(str(dest))
    assert "," in csv_str


def test_roundtrip_returns_dict(tmp_path):
    src = _make_tsv(tmp_path)
    dest2 = tmp_path / "copy.tsv"
    result = roundtrip(str(src), str(dest2))
    assert isinstance(result, dict)
    assert result["row_count"] == 3


def test_append_rows_increases_count(tmp_path):
    dest = _make_tsv(tmp_path)
    result = append_rows(str(dest), [["Dave", "95"], ["Eve", "60"]])
    assert result["row_count"] == 5


def test_get_column_values_names(tmp_path):
    dest = _make_tsv(tmp_path)
    vals = get_column_values(str(dest), "name")
    assert vals == ["Alice", "Bob", "Carol"]
