"""Tests for tsv.tsv_parser.sum_column_tsv() — Sprint 9, R146."""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(_REPO))

from src.python.tsv.tsv_parser import TsvError, sum_column_tsv

TSV_DATA = b"name\tscore\nAlice\t10\nBob\t20\nCharlie\t30\n"


def test_sum_numeric_column():
    assert sum_column_tsv(TSV_DATA, "score") == 60.0


def test_sum_returns_float():
    assert isinstance(sum_column_tsv(TSV_DATA, "score"), float)


def test_sum_skips_non_numeric():
    data = b"name\tscore\nAlice\t10\nBob\tnope\nCharlie\t5\n"
    assert sum_column_tsv(data, "score") == 15.0


def test_invalid_column_raises():
    try:
        sum_column_tsv(TSV_DATA, "nonexistent")
        assert 1 == 0, "Expected TsvError"

    except TsvError:
        pass


def test_empty_column():
    # Header detected only when there are 2+ equal-width rows
    data = b"name\tscore\nAlice\t\n"
    assert sum_column_tsv(data, "score") == 0.0


def test_negative_values():
    data = b"name\tscore\nA\t-5\nB\t10\n"
    assert sum_column_tsv(data, "score") == 5.0
