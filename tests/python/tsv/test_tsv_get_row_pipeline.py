"""
test_tsv_get_row_pipeline.py -- TSV get row pipeline.

Sprint: UNBOUNDED-AUTONOMOUS-CONVEYOR-WAVE-70
Tests get_row list, get_row index 0, get_row_by_key found, get_row_by_key None,
roundtrip row count.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import (
    get_row,
    get_row_by_key,
    roundtrip,
    write_tsv,
)

_HEADERS = ["name", "dept", "score"]
_ROWS = [["Alice", "eng", "90"], ["Bob", "mkt", "70"], ["Carol", "eng", "80"]]
_TSV_DATA = b"name\tdept\tscore\nAlice\teng\t90\nBob\tmkt\t70\nCarol\teng\t80\n"


def test_get_row_list():
    result = get_row(_TSV_DATA, 0)
    assert isinstance(result, list)


def test_get_row_index_0():
    result = get_row(_TSV_DATA, 0)
    assert result[0] == "Alice"


def test_get_row_by_key_found():
    result = get_row_by_key(_TSV_DATA, "name", "Bob")
    assert result is not None
    assert result[1] == "mkt"


def test_get_row_by_key_none():
    result = get_row_by_key(_TSV_DATA, "name", "Zara")
    assert result is None


def test_roundtrip_row_count(tmp_path):
    dest = tmp_path / "rt.tsv"
    write_tsv(_ROWS, str(tmp_path / "src.tsv"), headers=_HEADERS)
    result = roundtrip(str(tmp_path / "src.tsv"), str(dest))
    assert result["row_count"] == 3
