"""Tests for tsv.tsv_parser.get_row_by_key() — Sprint 6, R140."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, get_row_by_key


TSV_DATA = b"name\tage\tcity\nAlice\t30\tLondon\nBob\t25\tParis\nCharlie\t40\tLondon\n"
TSV_NO_HEADER = b"Alice\t30\nBob\t25\n"


def test_find_by_name():
    row = get_row_by_key(TSV_DATA, "name", "Alice")
    assert row == ["Alice", "30", "London"]


def test_find_by_city():
    row = get_row_by_key(TSV_DATA, "city", "Paris")
    assert row == ["Bob", "25", "Paris"]


def test_find_first_match():
    # "London" appears twice; should return first
    row = get_row_by_key(TSV_DATA, "city", "London")
    assert row == ["Alice", "30", "London"]


def test_not_found_returns_none():
    row = get_row_by_key(TSV_DATA, "name", "Dave")
    assert row is None


def test_no_header_raises():
    try:
        get_row_by_key(TSV_NO_HEADER, "name", "Alice")
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_unknown_column_raises():
    try:
        get_row_by_key(TSV_DATA, "unknown_col", "x")
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_find_by_age():
    row = get_row_by_key(TSV_DATA, "age", "25")
    assert row is not None
    assert row[0] == "Bob"
