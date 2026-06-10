"""Tests for tsv.tsv_parser.drop_column() — Sprint 8, R144."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, drop_column

TSV_DATA = b"name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\n"


def test_drop_middle_column():
    model = drop_column(TSV_DATA, "age")
    assert model["headers"] == ["name", "city"]
    assert model["rows"][0] == ["Alice", "London"]


def test_drop_first_column():
    model = drop_column(TSV_DATA, "name")
    assert model["headers"] == ["age", "city"]
    assert model["rows"][0] == ["30", "London"]


def test_drop_last_column():
    model = drop_column(TSV_DATA, "city")
    assert model["headers"] == ["name", "age"]
    assert model["rows"][0] == ["Alice", "30"]


def test_row_count_unchanged():
    model = drop_column(TSV_DATA, "age")
    assert len(model["rows"]) == 2


def test_invalid_column_raises():
    try:
        drop_column(TSV_DATA, "missing_col")
        assert False, "Expected TsvError"
    except TsvError:
        pass


def test_returns_dict():
    result = drop_column(TSV_DATA, "age")
    assert isinstance(result, dict)
    assert "headers" in result
