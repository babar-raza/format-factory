"""Tests for tsv.tsv_parser.column_count() — Sprint 12, R152."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import column_count


def test_three_columns():
    data = b"a\tb\tc\n1\t2\t3\n"
    assert column_count(data) == 3


def test_one_column():
    data = b"name\nAlice\nBob\n"
    assert column_count(data) == 1


def test_no_headers():
    data = b"only_one_row\n"
    # single row — no header detected (need at least 2 equal-width rows)
    assert column_count(data) == 0


def test_returns_int():
    data = b"x\ty\n1\t2\n"
    assert isinstance(column_count(data), int)


def test_two_columns():
    data = b"name\tscore\nAlice\t90\nBob\t85\n"
    assert column_count(data) == 2
