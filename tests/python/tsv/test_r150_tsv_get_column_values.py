"""Tests for tsv.tsv_parser.get_column_values() — Sprint 11, R150."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, get_column_values

TSV_BYTES = b"name\tscore\nAlice\t90\nBob\t85\nCarol\t92\n"


def test_returns_name_column():
    result = get_column_values(TSV_BYTES, "name")
    assert result == ["Alice", "Bob", "Carol"]


def test_returns_score_column():
    result = get_column_values(TSV_BYTES, "score")
    assert result == ["90", "85", "92"]


def test_missing_column_raises():
    try:
        get_column_values(TSV_BYTES, "missing")
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_returns_list():
    assert isinstance(get_column_values(TSV_BYTES, "name"), list)


def test_empty_cells_included():
    data = b"a\tb\nX\t\nY\tZ\n"
    result = get_column_values(data, "b")
    assert result == ["", "Z"]
