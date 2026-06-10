"""Tests for tsv.tsv_parser.sort_rows() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, sort_rows

TSV_DATA = b"name\tage\nCharlie\t30\nAlice\t25\nBob\t35\n"


def test_sort_by_name_asc():
    model = sort_rows(TSV_DATA, "name")
    assert model["rows"][0][0] == "Alice"
    assert model["rows"][1][0] == "Bob"
    assert model["rows"][2][0] == "Charlie"


def test_sort_by_name_desc():
    model = sort_rows(TSV_DATA, "name", reverse=True)
    assert model["rows"][0][0] == "Charlie"


def test_row_count_unchanged():
    model = sort_rows(TSV_DATA, "name")
    assert len(model["rows"]) == 3


def test_headers_preserved():
    model = sort_rows(TSV_DATA, "age")
    assert model["headers"] == ["name", "age"]


def test_invalid_column_raises():
    try:
        sort_rows(TSV_DATA, "nonexistent")
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_returns_dict():
    result = sort_rows(TSV_DATA, "name")
    assert isinstance(result, dict)
    assert "rows" in result
